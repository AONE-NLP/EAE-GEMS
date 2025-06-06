import argparse
import os
import sys
import logging
import pickle
from functools import partial
import time
from tqdm import tqdm
from collections import Counter
import random
import numpy as np

os.environ["CUDA_DEVICE_ORDER"] = 'PCI_BUS_ID'

import torch
from torch.utils.data import DataLoader
import torch.nn.functional as F
import pytorch_lightning as pl
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.callbacks.progress import TQDMProgressBar
from pytorch_lightning.callbacks import LearningRateMonitor

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


from transformers import AdamW, T5Tokenizer
from t5 import MyT5ForConditionalGeneration
from transformers import get_linear_schedule_with_warmup

from data_utils import ABSADataset, task_data_list, cal_entropy
from const import *
from data_utils import read_line_examples_from_json_file
from eval_utils import compute_scores, extract_spans_para
logging.getLogger("pytorch_lightning").setLevel(logging.INFO)
logger = logging.getLogger("pytorch_lightning.core")


def set_seed(seed: int = 42) -> None:
    np.random.seed(seed)
    random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    os.environ["PYTHONHASHSEED"] = str(seed)
    print(f"Random seed set as {seed}")


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", default="../data/", type=str)
    parser.add_argument(
        "--task",
        default='eae',
        type=str,
        help="task")
    parser.add_argument(
        "--dataset",
        default='ere-en',
        type=str,
        help="The name of the dataset you saved in ./data/eae")
    parser.add_argument(
        "--eval_data_split",
        default='test',
        choices=["test", "dev"],
        type=str,
    )
    parser.add_argument("--model_name_or_path",
                        default='../model/t5-large',
                        type=str,
                        help="Path to pre-trained model or shortcut name")
    parser.add_argument("--output_dir",
                        default='outputs/temp',
                        type=str,
                        help="Output directory")
    parser.add_argument("--load_ckpt_name",
                        default=None,
                        type=str,
                        help="load ckpt path")
    parser.add_argument("--do_train",
                        action='store_true',
                        help="Whether to run training.")
    parser.add_argument(
        "--do_inference",
        default=True,
        help="Whether to run inference with trained checkpoints")
    parser.add_argument("--max_seq_length", default=250, type=int)
    parser.add_argument("--n_gpu", default=0)
    parser.add_argument("--train_batch_size",
                        default=8,
                        type=int,
                        help="Batch size per GPU/CPU for training.")
    parser.add_argument("--eval_batch_size",
                        default=8,
                        type=int,
                        help="Batch size per GPU/CPU for evaluation.")
    parser.add_argument(
        '--gradient_accumulation_steps',
        type=int,
        default=1,
        help=
        "Number of updates steps to accumulate before performing a backward/update pass."
    )
    parser.add_argument("--learning_rate", default=1e-4, type=float)
    parser.add_argument("--num_train_epochs",
                        default=20,
                        type=int,
                        help="Total number of training epochs to perform.")
    parser.add_argument('--seed',
                        type=int,
                        default=25,
                        help="random seed for initialization")
    parser.add_argument("--weight_decay", default=0.0, type=float)
    parser.add_argument("--adam_epsilon", default=1e-8, type=float)
    parser.add_argument("--warmup_steps", default=0.0, type=float)
    parser.add_argument("--top_k", default=1, type=int)
    parser.add_argument("--multi_path", action='store_true')
    parser.add_argument("--num_path", default=1, type=int)
    parser.add_argument("--beam_size", default=1, type=int)
    parser.add_argument("--save_top_k", default=0, type=int)
    parser.add_argument("--check_val_every_n_epoch", default=10, type=int)
    parser.add_argument("--single_view_type",
                    default="rank",
                    choices=["rank", "rand", "heuristic"],
                    type=str)
    parser.add_argument("--ctrl_token",
                        default="post",
                        choices=["post", "pre", "none"],
                        type=str, help='Place prompt in the sentence, and the default post means that it is placed at the end of the sentence')
    parser.add_argument("--head",
                        default=4,
                        type=int, help='cross attention acts on event description and original input sentences, the number of attention heads passed here')
    
    
    parser.add_argument("--sort_label",
                        action='store_true',
                        help="sort tuple by order of appearance")
    parser.add_argument("--load_path_cache",
                        action='store_true',
                        help="load decoded path from cache")
    parser.add_argument("--lowercase", action='store_true')
    parser.add_argument("--multi_task", action='store_true')
    parser.add_argument("--constrained_decode",
                        default="True",
                        type=str,
                        help='constrained decoding when evaluating')
    parser.add_argument('--agg_strategy', type=str, default='vote', choices=['vote', 'rand', 'heuristic', 'pre_rank', 'post_rank'])
    parser.add_argument("--data_ratio",
                        default=1.0,
                        type=float,
                        help="low resource data ratio")

    args = parser.parse_args()
    if not os.path.exists('./outputs'):
        os.mkdir('./outputs')

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    return args


class T5FineTuner(pl.LightningModule):
    """
    Fine tune a pre-trained T5 model
    """

    def __init__(self, config, tfm_model, tokenizer):
        super().__init__()
        self.save_hyperparameters(ignore=['tfm_model'])
        self.config = config
        self.model = tfm_model
        self.tokenizer = tokenizer

    def forward(self,
                input_ids,
                attention_mask=None,
                decoder_input_ids=None,
                decoder_attention_mask=None,
                labels=None,
                event_description_ids=None, 
                event_description_mask=None, 
                ):
        return self.model(
            input_ids,
            attention_mask=attention_mask,
            decoder_input_ids=decoder_input_ids,
            decoder_attention_mask=decoder_attention_mask,
            labels=labels,
            event_description_ids=event_description_ids, 
            event_description_mask=event_description_mask, 
        )

    def _step(self, batch):
        lm_labels = batch["target_ids"]
        lm_labels[lm_labels[:, :] == self.tokenizer.pad_token_id] = -100

        outputs = self(input_ids=batch["source_ids"],
                       attention_mask=batch["source_mask"],
                       labels=lm_labels,
                       decoder_attention_mask=batch['target_mask'],
                       event_description_ids=batch['event_description_ids'], 
                       event_description_mask=batch['event_description_mask'], 
                       ) 


        loss = outputs[0]
        return loss

    def training_step(self, batch, batch_idx):
        loss = self._step(batch)
        self.log("train_loss", loss)
        return loss

    def evaluate(self, batch, stage=None):
        outs = self.model.generate(input_ids=batch['source_ids'], 
                                   attention_mask=batch['source_mask'], 
                                   event_description_ids=batch['event_description_ids'],
                                   event_description_mask=batch['event_description_mask'],
                                   max_length=self.config.max_seq_length, 
                                   return_dict_in_generate=True,
                                   output_scores=True,
                                   num_beams=1) 
        dec = [
            self.tokenizer.decode(ids, skip_special_tokens=True)
            for ids in outs.sequences
        ]  
        target = [
            self.tokenizer.decode(ids, skip_special_tokens=True)
            for ids in batch["target_ids"]
        ] 
        scores, _, _ = compute_scores(dec, target, verbose=False)
        f1 = torch.tensor(scores['f1'], dtype=torch.float64)
        arg_I_f1 = torch.tensor(scores['arg_I_f1'], dtype=torch.float64)
        loss = self._step(batch) 

        if stage:
            self.log(f"{stage}_loss",
                     loss,
                     prog_bar=True,
                     on_step=False,
                     on_epoch=True)
            self.log(f"{stage}_arg_I_f1",
                     arg_I_f1,
                     prog_bar=True,
                     on_step=False,
                     on_epoch=True)
            self.log(f"{stage}_arg_C_f1",
                     f1,
                     prog_bar=True,
                     on_step=False,
                     on_epoch=True)

    def validation_step(self, batch, batch_idx):
        self.evaluate(batch, "val")

    def test_step(self, batch, batch_idx):
        self.evaluate(batch, "test")

    def configure_optimizers(self):
        """ Prepare optimizer and schedule (linear warmup and decay) """
        model = self.model
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [
                    p for n, p in model.named_parameters()
                    if not any(nd in n for nd in no_decay)
                ],
                "weight_decay":
                self.config.weight_decay,
            },
            {
                "params": [
                    p for n, p in model.named_parameters()
                    if any(nd in n for nd in no_decay)
                ],
                "weight_decay":
                0.0,
            },
        ]
        optimizer = AdamW(optimizer_grouped_parameters,
                          lr=self.config.learning_rate,
                          eps=self.config.adam_epsilon)
        scheduler = {
            "scheduler":
            get_linear_schedule_with_warmup(optimizer,
                                            **self.config.lr_scheduler_init),
            "interval":
            "step",
        }
        return [optimizer], [scheduler]

    def train_dataloader(self):
        print("load training data.")
        train_dataset = ABSADataset(tokenizer=self.tokenizer,
                                    task_name=args.task,
                                    data_name=args.dataset,
                                    data_type="train",
                                     top_k=self.config.top_k,
                                    args=self.config,
                                    max_len=self.config.max_seq_length)

        dataloader = DataLoader(
            train_dataset,
            batch_size=self.config.train_batch_size,
            drop_last=True
            if args.data_ratio > 0.3 else False, # don't drop on few-shot
            shuffle=True,
            num_workers=2)

        return dataloader

    def val_dataloader(self):
        val_dataset = ABSADataset(tokenizer=self.tokenizer,
                                  task_name=args.task,
                                  data_name=args.dataset,
                                  data_type="dev",
                                  top_k=self.config.num_path,
                                  args=self.config,
                                  max_len=self.config.max_seq_length)
        return DataLoader(val_dataset,
                          batch_size=self.config.eval_batch_size,
                          num_workers=2)

    @staticmethod
    def rindex(_list, _value):
        return len(_list) - _list[::-1].index(_value) - 1

    def prefix_allowed_tokens_fn(self, task, data_name, source_ids, batch_id,
                                 input_ids):
        """
        Constrained Decoding
        """
        dic = {"type_tokens":[], "all_tokens":{}, "role_tokens":[], 'special_tokens':[]} 
        type_tokens = []
        for i in cate_list_eae[data_name]:
            type_tokens.extend(self.tokenizer(i, return_tensors='pt')['input_ids'].tolist()[0]) 
        dic["type_tokens"] = type_tokens
        role_tokens = []
        for i in force_words_eae[task][data_name]:
            role_tokens.extend(self.tokenizer(i, return_tensors='pt')['input_ids'].tolist()[0]) 
        dic["role_tokens"] = role_tokens
        special_tokens_tokenize_res = []
        for w in ['[T','[A','[R','[SS']:
            special_tokens_tokenize_res.extend(self.tokenizer(w, return_tensors='pt')['input_ids'].tolist()[0])  
        special_tokens_tokenize_res = [r for r in special_tokens_tokenize_res if r != 784] 
        dic['special_tokens'] = special_tokens_tokenize_res                                                
        import json
        with open("./force_tokens.json", 'w', encoding='utf-8') as f:
            json.dump(dic, f, indent=4)
            
        force_tokens = dic
        to_id = {
            'T': [382], # 'T'  TriggeR
            'A': [188],  # 'A' ArgumenT
            'R': [448],  # 'R' Argument Role         
            'SS': [4256],  # 'SS'
            'EP': [8569],  # 'EP' [SSEP]
            '[': [784],  # '▁['
            ']': [908],  # ']'
            'it': [34],  # '▁it'
            'null': [206,195],  # '▁nu', 'll'
        }
        left_brace_index = (input_ids == to_id['['][0]).nonzero()
        right_brace_index = (input_ids == to_id[']'][0]).nonzero()
        num_left_brace = len(left_brace_index)
        num_right_brace = len(right_brace_index)
        last_right_brace_pos = right_brace_index[-1][
            0] if right_brace_index.nelement() > 0 else -1
        last_left_brace_pos = left_brace_index[-1][
            0] if left_brace_index.nelement() > 0 else -1
        cur_id = input_ids[-1]

        if cur_id in to_id['[']:
            return force_tokens['special_tokens']
        elif cur_id in to_id['T'] + to_id['A'] + to_id['R'] + to_id['EP']:  
            return to_id[']']  
        elif (cur_id in to_id['SS']): 
            return to_id['EP'] 
        if last_left_brace_pos == -1: 
            return to_id['['] + [1]   # start of sentence: [      ; [1] -> '</s>'
        elif (last_left_brace_pos != -1 and last_right_brace_pos == -1) \
            or last_left_brace_pos > last_right_brace_pos:
            return to_id[']']  # ]
        else:
            cur_term = input_ids[last_left_brace_pos + 1]  

        ret = []
        if cur_term in to_id['T']:  # trigger
            force_list = source_ids[batch_id].tolist() + to_id['null']
            ret = force_list  
        elif cur_term in to_id['SS']:
            ret = [3] + to_id[']'] + [1]   
        elif cur_term in to_id['R']:  # argument role
            ret = force_tokens['role_tokens']
        elif cur_term in to_id['A']:  # argument
            force_list = source_ids[batch_id].tolist() + to_id['null'] 
            if task == "eae":
                force_list.extend(to_id['null'])  # null
            ret = force_list
        else:
            raise ValueError(cur_term)

        if num_left_brace == num_right_brace: 
            ret = set(ret)
            ret.discard(to_id[']'][0]) # remove ]
            for w in force_tokens['special_tokens']:
                ret.discard(w)
            ret = list(ret)
        elif num_left_brace > num_right_brace:
            ret += to_id[']'] 
        else:
            raise ValueError
        ret.extend(to_id['['] + [1]) # add [  
        return ret 


def evaluate(model, task, data, data_type):
    """
    Compute scores given the predictions and gold labels
    """
    print("src -> main.py -> def evaluate workspace -> os.path.abspath(os.curdir) : ", os.path.abspath(os.curdir))
    tasks, datas, sents, _ = read_line_examples_from_json_file(
        f'../data/{task}/{data}/{data_type}.json', task, data, lowercase=args.lowercase)

    outputs, targets, probs = [], [], []
    dec_outputs = [] 
    num_path = args.num_path
    if task in ["eae"]: 
        num_path = min(5, num_path)

    cache_file = os.path.join(
        args.output_dir, "result_{}{}{}_{}_path{}_beam{}.pickle".format(
            "best_" if args.load_ckpt_name else "",
            "cd_" if args.constrained_decode else "", task, data, num_path,
            args.beam_size))
    if args.load_path_cache:
        with open(cache_file, 'rb') as handle:
            (outputs, targets, probs) = pickle.load(handle)
    else:
        dataset = ABSADataset(model.tokenizer,
                              task_name=task,
                              data_name=data,
                              data_type=data_type,
                              top_k=num_path,
                              args=args,
                              max_len=args.max_seq_length)
        data_loader = DataLoader(dataset,
                                 batch_size=args.eval_batch_size,
                                 num_workers=2)
        model.model.to(_device)
        model.model.eval()

        for batch in tqdm(data_loader):
            outs = model.model.generate(
                input_ids=batch['source_ids'].to(_device),
                attention_mask=batch['source_mask'].to(_device),
                event_description_ids=batch["event_description_ids"].to(_device),
                event_description_mask=batch["event_description_mask"].to(_device),
                max_length=args.max_seq_length,
                num_beams=args.beam_size,
                early_stopping=True,
                return_dict_in_generate=True,
                output_scores=True,
                prefix_allowed_tokens_fn=partial(
                    model.prefix_allowed_tokens_fn, task, data,
                    batch['source_ids']) if args.constrained_decode else None,
            ) 

            dec = [
                model.tokenizer.decode(ids, skip_special_tokens=True)
                for ids in outs.sequences
            ]
            target = [
                model.tokenizer.decode(ids, skip_special_tokens=True)
                for ids in batch["target_ids"]
            ]
            dec_outputs.extend(dec) 
            outputs.extend(dec)
            targets.extend(target)


            stacked_tensor = torch.stack(outs.scores, dim=1)
            max_values, _ = torch.max(stacked_tensor, dim=2)
            sum_max_values = torch.sum(max_values, dim=1)
            probs.extend(sum_max_values.tolist())  
        with open(cache_file, 'wb') as handle:
            pickle.dump((outputs, targets, probs), handle)

    if args.multi_path:
        targets = targets[::num_path]  
        _outputs = outputs # backup
        outputs = [] # new outputs
        new_targets = [] 

        if args.agg_strategy == 'post_rank':
            inputs = [ele for ele in sents for _ in range(num_path)]
            assert len(_outputs) == len(inputs), (len(_outputs), len(inputs))
            preds = [[o] for o in _outputs] 
            model_path = os.path.join(args.output_dir, "final")
            scores = cal_entropy(inputs, preds, model_path, model.tokenizer)

        for i in range(0, len(targets)):
            o_idx = i * num_path
            multi_outputs = _outputs[o_idx:o_idx + num_path]


            if args.agg_strategy == 'rand':
                outputs.append(random.choice(multi_outputs))
                continue

            elif args.agg_strategy == 'vote': 
                all_quads = []
                for s in multi_outputs:
                    all_quads.extend(
                        extract_spans_para(seq=s, seq_type='pred'))

                output_quads = []
                counter = dict(Counter(all_quads))
                for quad, count in counter.items():
                    if count >= len(multi_outputs) / 2:
                        output_quads.append(quad)
                output = []
                for q in output_quads:
                    t, a, r = q
                    if task == "eae":
                        if ('null' not in [t, a, r]) and ('' not in [t, a, r]): 
                            output.append(f'[T] {t} [A] {a} [R] {r}')
                    else:
                        raise NotImplementedError                            


                target_quads = extract_spans_para(seq=targets[i],
                                                seq_type='gold')
                
                target = []

                for q in target_quads:
                    t, a, r = q
                    if task == 'eae':
                        if ('null' not in [t, a, r]) and ('' not in [t, a, r]): 
                            target.append(f'[T] {t} [A] {a} [R] {r}')                        

                if sorted(target_quads) != sorted(output_quads):
                    print("task, data:", tasks[i], datas[i])
                    print("target:", sorted(target))
                    print('output:', sorted(output))
                    print("sent:", " ".join(sents[i]))
                    print("counter:", counter)
                    print("output quads:", output)
                    print("multi_path:", multi_outputs)
                    print()
                output_str = " [SSEP] ".join(
                    output) if output else multi_outputs[0]

                outputs.append(output_str)
                new_targets.append(" [SSEP] ".join(target))
    labels_counts = Counter([len(l.split('[SSEP]')) for l in outputs])
    print("pred labels count", labels_counts)
    scores, all_labels, all_preds = compute_scores(outputs,
                                                   new_targets,
                                                   verbose=True)
    for i in range(len(all_labels)):
        print("Line ", i, " : ")
        print("sents : ", " ".join(sents[i]))
        print("Ground Truth : ")
        print("new_targets : ", new_targets[i])
        print("all_labels : ", all_labels[i])
        print("Model Generate : ")
        if i*num_path+3 < len(all_labels)*num_path:
            print("dec_outputs[i*num_path] : ", dec_outputs[i*num_path])
            print("dec_outputs[i*num_path+1] : ", dec_outputs[i*num_path+1])
            print("dec_outputs[i*num_path+2] : ", dec_outputs[i*num_path+2])
            print("dec_outputs[i*num_path+3] : ", dec_outputs[i*num_path+3])
        print("outputs : ", outputs[i])
        print("all_preds : ", all_preds[i])
        print()


    return scores


def train_function(args):
    if args.do_train:
        print("\n", "=" * 30, f"NEW EXP: {args.task} on {args.dataset}",
              "=" * 30, "\n")
        tokenizer = T5Tokenizer.from_pretrained(args.model_name_or_path, local_files_only=True if args.model_name_or_path not in ["t5-large","t5-base"] else False)
        print(f"Here is an example (from the dev set):")
        dataset = ABSADataset(tokenizer=tokenizer,
                              task_name=args.task,
                              data_name=args.dataset,
                              data_type='train',
                              top_k=args.top_k,
                              args=args,
                              max_len=args.max_seq_length)
        for i in range(0, min(10, len(dataset))): 
            data_sample = dataset[i]
            print(
                'Input :',
                tokenizer.decode(data_sample['source_ids'],
                                 skip_special_tokens=True))
            print('Input :',
                  tokenizer.convert_ids_to_tokens(data_sample['source_ids']))
            print(
                'Output:',
                tokenizer.decode(data_sample['target_ids'],
                                 skip_special_tokens=True))
            print()

        print("\n****** Conduct Training ******")
        tfm_model = MyT5ForConditionalGeneration.from_pretrained(
            args.model_name_or_path, local_files_only=True if args.model_name_or_path != "t5-large" else False, \
                head = args.head
                )
        model = T5FineTuner(args, tfm_model, tokenizer)
        train_loader = model.train_dataloader()
        t_total = ((len(train_loader.dataset) //
                    (args.train_batch_size * max(1, args.n_gpu))) //
                   args.gradient_accumulation_steps *
                   float(args.num_train_epochs))

        args.lr_scheduler_init = {
            "num_warmup_steps": args.warmup_steps,
            "num_training_steps": t_total
        }

        checkpoint_callback = pl.callbacks.ModelCheckpoint(
            dirpath=args.output_dir,
            filename='{epoch}-{val_arg_C_f1:.2f}-{val_loss:.2f}',
            monitor='val_arg_C_f1',
            mode='max',
            save_top_k=args.save_top_k,
            save_last=False)
        
        early_stop_callback = EarlyStopping(monitor="val_arg_C_f1",
                                            min_delta=0.00,
                                            patience=20,
                                            verbose=True,
                                            mode="max")
        lr_monitor = LearningRateMonitor(logging_interval='step')
        train_params = dict(
            accelerator="gpu",
            devices=1,
            default_root_dir=args.output_dir,
            accumulate_grad_batches=args.gradient_accumulation_steps,
            gradient_clip_val=1.0,
            max_epochs=args.num_train_epochs,
            check_val_every_n_epoch=args.check_val_every_n_epoch,
            callbacks=[
                checkpoint_callback, early_stop_callback,
                TQDMProgressBar(refresh_rate=10), lr_monitor
            ],
        )

        trainer = pl.Trainer(**train_params)

        trainer.fit(model) 
        model.model.save_pretrained(os.path.join(args.output_dir, "final"))
        tokenizer.save_pretrained(os.path.join(args.output_dir, "final"))
        print("Finish training and saving the model!")

    if args.do_inference:
        print("\n****** Conduct inference on trained checkpoint ******")
        print(f"Load trained model from {args.output_dir}")
        print(
            'Note that a pretrained model is required and `do_true` should be False'
        )
        model_path = os.path.join(args.output_dir, "final")
        print(type(model_path))
        print(model_path)
        print(os.path.abspath(os.curdir))
        tokenizer = T5Tokenizer.from_pretrained(model_path)
        tfm_model = MyT5ForConditionalGeneration.from_pretrained(model_path, head = args.head)
        model = T5FineTuner(args, tfm_model, tokenizer)

        if args.load_ckpt_name:
            ckpt_path = os.path.join(args.output_dir, args.load_ckpt_name)
            print("Loading ckpt:", ckpt_path)
            checkpoint = torch.load(ckpt_path)
            model.load_state_dict(checkpoint["state_dict"])

        log_file_path = os.path.join(args.output_dir, "result.txt")
        with open(log_file_path, "a+") as f:
            config_str = f"seed: {args.seed}, beam: {args.beam_size}, constrained: {args.constrained_decode}\n"
            print(config_str)
            f.write(config_str)

            if args.multi_task:
                f1s = []
                for task in task_data_list:
                    for data in task_data_list[task]:
                        scores = evaluate(model, task, data, data_type=args.eval_data_split)
                        print(task, data, scores)
                        exp_results = "{} {} Arg_C : arg_prec: {:.2f} arg_rec: {:.2f} arg_f1: {:.2f} Arg_I: precision: {:.2f} recall: {:.2f} F1 = {:.2f}".format(
                            args.eval_data_split, args.agg_strategy, scores['arg_I_prec'], scores['arg_I_recall'], scores['arg_I_f1'], scores['precision'], scores['recall'], scores['f1'])
                        f.write(f"{task}: \t{data}: \t{exp_results}\n")
                        f.flush()
                        f1s.append(scores['f1'])
                f.write(f"Average F1: \t{sum(f1s) / len(f1s)}\n")
                f.flush()
            else:
                scores = evaluate(model,
                                  args.task,
                                  args.dataset,
                                data_type=args.eval_data_split) 

                exp_results = "{} {} Arg_C : arg_prec: {:.2f} arg_rec: {:.2f} arg_f1: {:.2f} Arg_I: precision: {:.2f} recall: {:.2f} F1 = {:.2f}".format(
                            args.eval_data_split, args.agg_strategy, scores['arg_I_prec'], scores['arg_I_recall'], scores['arg_I_f1'], scores['precision'], scores['recall'], scores['f1'])
                print(exp_results)
                f.write(exp_results + "\n")
                f.flush()
    return scores['f1']


if __name__ == '__main__':
    args = init_args()
    set_seed(args.seed)
    train_function(args)
