import random
import json
import numpy as np
from itertools import permutations
import torch
from torch.utils.data import Dataset

from t5_score import MyT5ForConditionalGenerationScore
from const import *
import random

def get_element_tokens(task):
    dic = {
        "eae":
            ["[T]", "[TT]", "[A]", "[R]"] 

    }
    return dic[task]


def get_orders(task, data, args, sents, labels):

    if args.single_view_type == 'rank': 
        orders = optim_orders_all_eae[task][data]
        
        return orders
    
def read_line_examples_from_file(data_path,
                                 task_name,
                                 data_name,
                                 lowercase,
                                 silence=True):
    """
    Read data from file, each line is: sent####labels
    Return List[List[word]], List[Tuple]
    """
    tasks, datas = [], []
    sents, labels = [], []
    with open(data_path, 'r', encoding='UTF-8') as fp:
        words, labels = [], []
        for line in fp:
            line = line.strip()
            if lowercase:
                line = line.lower()
            if "unified" in task_name:
                _task, _data, line = line.split("\t")
                tasks.append(_task)
                datas.append(_data)
            else:
                tasks.append(task_name)
                datas.append(data_name)
            if line != '':
                words, tuples = line.split('####')
                sents.append(words.split())
                labels.append(eval(tuples)) 
    if silence:
        print(f"Total examples = {len(sents)}")
    return tasks, datas, sents, labels  


'''
{"sentence": ["We", "'re", "talking", "about", "possibilities", "of", "full", "scale", "war", "with", "former", "Congressman", "Tom", "Andrews", ",", "Democrat", "of", "Maine", "."], 
 "events": [{"trigger": {"start": 8, "end": 9, "words": "war", "type": "Conflict.Attack"}, 
             "arguments": []}, 
            {"trigger": {"start": 10, "end": 11, "words": "former", "type": "Personnel.End-Position"}, 
             "arguments": [{"head": 12, "tail": 14, "words": "Tom Andrews", "role": "Person"}, 
                           {"head": 17, "tail": 18, "words": "Maine", "role": "Entity"}]}]}
'''

def read_line_examples_from_json_file(data_path,
                                 task_name,
                                 data_name,
                                 lowercase,
                                 silence=True):
    """
    Read data from file, each line is: sent####labels
    Return List[List[word]], List[Tuple]
    """
    tasks, datas = [], []
    sents, labels = [], []
    import os
    print(os.path.abspath(os.curdir))
    print(data_path)
    with open(data_path, 'r', encoding='UTF-8') as fp:
        words, labels = [], []
        for line in fp:
            line = json.loads(line)
            words = line["sentence"]
            events = line["events"]



            if lowercase:
                words = [word.lower() for word in words]
                if events != []:
                    for i in range(len(events)):
                        events[i]["trigger"]["words"] = events[i]["trigger"]["words"].lower()
                        for j in range(len(events[i]["arguments"])):
                            events[i]["arguments"][j]["words"] = events[i]["arguments"][j]["words"].lower()
                            
            words.insert(events[0]["trigger"]["start"], "[T]")
            words.insert(events[0]["trigger"]["end"] + 1, "[/T]")
                        

            if "unified" in task_name:
                _task, _data, line = line.split("\t")
                tasks.append(_task)
                datas.append(_data)
            else:
                tasks.append(task_name)
                datas.append(data_name)
            

            if line != {} or line != None:
                sents.append(words)
                labels.append(events)

    if silence:
        print(f"Total examples = {len(sents)}")
    return tasks, datas, sents, labels  


def cal_entropy(inputs, preds, model_path, tokenizer, device=torch.device('cuda')):
    all_entropy = []
    model = MyT5ForConditionalGenerationScore.from_pretrained(model_path).to(
        device)
    batch_size = 8
    _inputs = [' '.join(s) for s in inputs]
    _preds = [' '.join(s) for s in preds]
    for id in range(0, len(inputs), batch_size):
        in_batch = _inputs[id: min(id + batch_size, len(inputs))]
        pred_batch = _preds[id: min(id + batch_size, len(inputs))]
        assert len(in_batch) == len(pred_batch)
        tokenized_input = tokenizer.batch_encode_plus(in_batch,
                                                      max_length=250,
                                                      padding="max_length",
                                                      truncation=True,
                                                      return_tensors="pt")
        tokenized_target = tokenizer.batch_encode_plus(pred_batch,
                                                       max_length=250,
                                                       padding="max_length",
                                                       truncation=True,
                                                       return_tensors="pt")

        target_ids = tokenized_target["input_ids"].to(device)

        target_ids[target_ids[:, :] == tokenizer.pad_token_id] = -100
        outputs = model(
            input_ids=tokenized_input["input_ids"].to(device),
            attention_mask=tokenized_input["attention_mask"].to(device),
            labels=target_ids,
            decoder_attention_mask=tokenized_target["attention_mask"].to(device))

        loss, entropy = outputs[0]
        all_entropy.extend(entropy)
    return all_entropy




def get_para_targets_eae(sents, labels, data_name, data_type, top_k, task, args):
    """
    Obtain the target sentence under the paraphrase paradigm
    """
    targets = []
    new_sents = []

    event_descriptions = []
    top_k = min(10, top_k)    
    optim_orders = get_orders(task, data_name, args, sents, labels)[:top_k]
    
    for i in range(len(sents)):
        label = labels[i] 
        cur_sent = sents[i]
        cur_sent_str = " ".join(cur_sent) 
        event_description = ere_event_description_dict[label[0]["trigger"]["type"]]

        '''
        {"sentence": ["The", "call", "reflected", "the", "insistent", "demand", "made", "by", "the", "three", "leaders", "before", "the", 
                      "US", "-", "British", "invasion", "of", "Iraq", "that", "UN", "approval", "was", "essential", "for", "any", "mission", 
                      "to", "topple", "Iraqi", "President", "Saddam", "Hussein", "."], 
         "events": [{"trigger": {"start": 16, "end": 17, "words": "invasion", "type": "Conflict.Attack"}, 
                     "arguments": [{"head": 13, "tail": 14, "words": "US", "role": "Attacker"}, 
                                   {"head": 15, "tail": 16, "words": "British", "role": "Attacker"}]}]}
        '''

        quad_list = []
        quad_list_sent_prompt = []

        if label != []:
            for event in label:

                element_list_t = {}
                element_list_t["[T]"] = "[T] {}".format(event["trigger"]["words"])

                element_list_a = {}

                element_event_all_arg_dict = {}
                event_args = [event_arg for event_arg in ere_event_type_argument_role_dict[event["trigger"]["type"]]]
                random.shuffle(event_args)

                if event["arguments"] != []:
                    
                    for arg in event["arguments"]: 
                        if arg["role"] not in element_event_all_arg_dict.keys():
                            element_event_all_arg_dict[arg["role"]] = []
                            element_event_all_arg_dict[arg["role"]].append(arg["words"])
                        else:
                            element_event_all_arg_dict[arg["role"]].append(arg["words"])
                
                for event_arg in event_args:
                    if event_arg not in element_event_all_arg_dict.keys():
                        element_event_all_arg_dict[event_arg] = []
                        element_event_all_arg_dict[event_arg].append("null")
                element_list_a["[A] [R]"] = []
                element_list_a["[R] [A]"] = []

                for arg in event_args: 
                    tmp = ["[A] {} [R] {}".format(arg_word, arg) for arg_word in element_event_all_arg_dict[arg]]
                    element_list_a["[A] [R]"].append(" [SSEP] ".join(tmp))

                    tmp = ["[R] {} [A] {}".format(arg, arg_word) for arg_word in element_event_all_arg_dict[arg]]
                    element_list_a["[R] [A]"].append(" [SSEP] ".join(tmp))                    

                element_list_sent_prompt = {}
                element_list_sent_prompt["[A] [R]"] = ["[A] {} [R] {}".format("", arg_role) for arg_role in event_args]
                element_list_sent_prompt["[R] [A]"] = ["[R] {} [A] {}".format(arg_role, "") for arg_role in event_args]


                permute_object = {} 
                permute_object_sent_prompt = {}

                for order in optim_orders: 
                    if order[1] == 'T':
                        first_order = " ".join(order.split(" ")[:1]) 
                        second_order = " ".join(order.split(" ")[1:])
                    else:
                        first_order = " ".join(order.split(" ")[:2])
                        second_order = " ".join(order.split(" ")[2:]) 

                    if first_order[1] == 'T': 
                        permute_object[order] = element_list_t[first_order] + " [SSEP] " + " [SSEP] ".join(element_list_a[second_order])
                        permute_object_sent_prompt[order] = element_list_t[first_order] + " [SSEP] " + " [SSEP] ".join(element_list_sent_prompt[second_order])
                    else:
                        permute_object[order] = " [SSEP] ".join(element_list_a[first_order]) + " [SSEP] " + element_list_t[second_order]
                        permute_object_sent_prompt[order] = " [SSEP] ".join(element_list_sent_prompt[first_order]) + " [SSEP] " + element_list_t[second_order]                        
                

                quad_list.append(permute_object)
                quad_list_sent_prompt.append(permute_object_sent_prompt)

        else: 
            element_list_t = {}
            element_list_a = {}

            element_list_t["[T]"] = "[T] null"
            element_list_a["[A] [R]"] = "[A] null [R] null"
            element_list_a["[R] [A]"] = "[R] null [A] null"  


            element_list_sent_prompt = {}
            element_list_sent_prompt["[A] [R]"] = "[A] {} [R] {}".format("null", "")
            element_list_sent_prompt["[R] [A]"] = "[R] {} [A] {}".format("", "null")

            permute_object = {} 
            permute_object_sent_prompt = {}

            for order in optim_orders: 

                if order[1] == 'T':
                    first_order = " ".join(order.split(" ")[:1]) 
                    second_order = " ".join(order.split(" ")[1:])
                else:
                    first_order = " ".join(order.split(" ")[:2])
                    second_order = " ".join(order.split(" ")[2:]) 

                if first_order[1] == 'T':
                    permute_object[order] = element_list_t[first_order] + " [SSEP] " + element_list_a[second_order]
                    permute_object_sent_prompt[order] = element_list_t[first_order] + " [SSEP] " + element_list_sent_prompt[second_order]
                else:
                    permute_object[order] = element_list_a[first_order] + " [SSEP] " + element_list_t[second_order]
                    permute_object_sent_prompt[order] = element_list_sent_prompt[first_order] + " [SSEP] " + element_list_t[second_order]  
                
            quad_list.append(permute_object) 
            quad_list_sent_prompt.append(permute_object_sent_prompt)
        for order in optim_orders:
            tar = []
            for each_q_dict in quad_list:
                tar.append(each_q_dict[order])
            targets.append(" [SSEP] ".join(tar))
        
            sent_prompt = []
            for each_q_sent_prompt_dict in quad_list_sent_prompt:
                sent_prompt.append(each_q_sent_prompt_dict[order])
            sent_prompt_str = " [SSEP] ".join(sent_prompt)

            new_sents.append((cur_sent_str + " " + sent_prompt_str).split(" "))
        
            event_descriptions.append(event_description)
        
    return new_sents, targets, event_descriptions


def get_para_targets_eae_dev(sents, labels, data_name, task, args):
    """
    Obtain the target sentence under the paraphrase paradigm
    """
    targets = []
    new_sents = []

    event_descriptions = []
    optim_orders = get_orders(task, data_name, args, sents=None, labels=None)
    top_order = optim_orders[0] 
    
    for i in range(len(sents)):
        label = labels[i] 
        cur_sent = sents[i]
        cur_sent_str = " ".join(cur_sent) 
        event_description = ere_event_description_dict[label[0]["trigger"]["type"]]

        '''
        {"sentence": ["The", "call", "reflected", "the", "insistent", "demand", "made", "by", "the", "three", "leaders", "before", "the", 
                      "US", "-", "British", "invasion", "of", "Iraq", "that", "UN", "approval", "was", "essential", "for", "any", "mission", 
                      "to", "topple", "Iraqi", "President", "Saddam", "Hussein", "."], 
         "events": [{"trigger": {"start": 16, "end": 17, "words": "invasion", "type": "Conflict.Attack"}, 
                     "arguments": [{"head": 13, "tail": 14, "words": "US", "role": "Attacker"}, 
                                   {"head": 15, "tail": 16, "words": "British", "role": "Attacker"}]}]}
        '''

        quad_list = []
        quad_list_sent_prompt = []

        if label != []:
            for event in label:

                element_list_t = {}
                element_list_t["[T]"] = "[T] {}".format(event["trigger"]["words"])

                element_list_a = {}

                element_event_all_arg_dict = {}
                event_args = [event_arg for event_arg in ere_event_type_argument_role_dict[event["trigger"]["type"]]]
                random.shuffle(event_args)


                if event["arguments"] != []:
                    
                    for arg in event["arguments"]: 
                        if arg["role"] not in element_event_all_arg_dict.keys():
                            element_event_all_arg_dict[arg["role"]] = []
                            element_event_all_arg_dict[arg["role"]].append(arg["words"])
                        else:
                            element_event_all_arg_dict[arg["role"]].append(arg["words"])
                
                for event_arg in event_args:
                    if event_arg not in element_event_all_arg_dict.keys():
                        element_event_all_arg_dict[event_arg] = []
                        element_event_all_arg_dict[event_arg].append("null")
                element_list_a["[A] [R]"] = []

                for arg in event_args: 
                    tmp = ["[A] {} [R] {}".format(arg_word, arg) for arg_word in element_event_all_arg_dict[arg]]
                    element_list_a["[A] [R]"].append(" [SSEP] ".join(tmp))

                element_list_sent_prompt = {}
                element_list_sent_prompt["[A] [R]"] = ["[A] {} [R] {}".format("", arg_role) for arg_role in event_args]



                permute_object = {} 
                permute_object_sent_prompt = {}
                if top_order[1] == 'T':
                    first_order = " ".join(top_order.split(" ")[:1]) 
                    second_order = " ".join(top_order.split(" ")[1:])
                else:
                    first_order = " ".join(top_order.split(" ")[:2])
                    second_order = " ".join(top_order.split(" ")[2:]) 

                if first_order[1] == 'T':   
                    permute_object[top_order] = element_list_t[first_order] + " [SSEP] " + " [SSEP] ".join(element_list_a[second_order])
                    permute_object_sent_prompt[top_order] = element_list_t[first_order] + " [SSEP] " + " [SSEP] ".join(element_list_sent_prompt[second_order])
                else:
                    permute_object[top_order] = " [SSEP] ".join(element_list_a[first_order]) + " [SSEP] " + element_list_t[second_order]
                    permute_object_sent_prompt[top_order] = " [SSEP] ".join(element_list_sent_prompt[first_order]) + " [SSEP] " + element_list_t[second_order]                        
                

                quad_list.append(permute_object)
                quad_list_sent_prompt.append(permute_object_sent_prompt)

        else: 
            element_list_t = {}
            element_list_a = {}

            element_list_t["[T]"] = "[T] null"
            element_list_a["[A] [R]"] = "[A] null [R] null"
            element_list_a["[R] [A]"] = "[R] null [A] null"  


            element_list_sent_prompt = {}
            element_list_sent_prompt["[A] [R]"] = "[A] {} [R] {}".format("null", "")
            element_list_sent_prompt["[R] [A]"] = "[R] {} [A] {}".format("", "null")


            permute_object = {} 
            permute_object_sent_prompt = {}

            if top_order[1] == 'T':
                first_order = " ".join(top_order.split(" ")[:1]) 
                second_order = " ".join(top_order.split(" ")[1:])
            else:
                first_order = " ".join(top_order.split(" ")[:2])
                second_order = " ".join(top_order.split(" ")[2:]) 

            if first_order[1] == 'T':
                permute_object[top_order] = element_list_t[first_order] + " [SSEP] " + element_list_a[second_order]
                permute_object_sent_prompt[top_order] = element_list_t[first_order] + " [SSEP] " + element_list_sent_prompt[second_order]
            else:
                permute_object[top_order] = element_list_a[first_order] + " [SSEP] " + element_list_t[second_order]
                permute_object_sent_prompt[top_order] = element_list_sent_prompt[first_order] + " [SSEP] " + element_list_t[second_order]  
                
            quad_list.append(permute_object) 
            quad_list_sent_prompt.append(permute_object_sent_prompt)

        tar = []
        for each_q_dict in quad_list:
            tar.append(each_q_dict[top_order])
        targets.append(" [SSEP] ".join(tar))
    
        sent_prompt = []
        for each_q_sent_prompt_dict in quad_list_sent_prompt:
            sent_prompt.append(each_q_sent_prompt_dict[top_order])
        sent_prompt_str = " [SSEP] ".join(sent_prompt)

        new_sents.append((cur_sent_str + " " + sent_prompt_str).split(" "))

        event_descriptions.append(event_description)
        
    return new_sents, targets, event_descriptions



def get_transformed_io(data_path, data_name, data_type, top_k, args):
    """
    The main function to transform input & target according to the task
    """
    tasks, datas, sents, labels = read_line_examples_from_json_file(
        data_path, args.task, args.dataset, args.lowercase)
    inputs = [s.copy() for s in sents]
    if data_type == 'train' and args.data_ratio != 1.0:
        num_sample = len(inputs)
        sample_indices = [i for i in range(len(inputs))]
        sample_inputs = [inputs[i] for i in sample_indices]
        sample_labels = [labels[i] for i in sample_indices]
        inputs, labels = sample_inputs, sample_labels
        print(
            f"Low resource: {args.data_ratio}, total train examples = {num_sample}")
        if num_sample <= 20:
            print("Labels:", sample_labels)

    if data_type == "train" or args.eval_data_split == "dev" or data_type == "test":
        new_inputs, targets, event_descriptions = get_para_targets_eae(inputs, labels, data_name,
                                               data_type, top_k, args.task,
                                               args)    
    else:
        new_inputs, targets, event_descriptions = get_para_targets_eae_dev(inputs, labels, data_name,
                                                   args.task, args)
    print(len(inputs), len(new_inputs), len(targets), len(event_descriptions))
    return new_inputs, targets, event_descriptions


def get_transformed_io_unified(data_path, task_name, data_name, data_type,
                               top_k, args):


    tasks, datas, sents, labels = read_line_examples_from_json_file(
        data_path, task_name, data_name, lowercase=args.lowercase)
    
    sents = [s.copy() for s in sents]
    new_inputs, targets = [], []
    for task, data, sent, label in zip(tasks, datas, sents, labels):
        if data_type == "train" or (data_type == "test" and args.multi_path):
            new_input, target = get_para_targets_eae([sent], [label], data,
                                                 data_type, top_k, task, args)
        else:
            new_input, target = get_para_targets_eae_dev([sent], [label], data,
                                                     task, args)
        new_inputs.extend(new_input)
        targets.extend(target)

    print("Ori sent size:", len(sents))
    print("Input size:", len(new_inputs), len(targets))
    print("Examples:")
    print(new_inputs[:10])
    print(targets[:10])

    return new_inputs, targets


class ABSADataset(Dataset):

    def __init__(self,
                 tokenizer,
                 task_name,
                 data_name,
                 data_type,
                 top_k,
                 args,
                 max_len=128):
        self.data_path = f'{args.data_path}/{task_name}/{data_name}/{data_type}.json'
        self.max_len = max_len
        self.tokenizer = tokenizer
        self.task_name = task_name
        self.data_name = data_name
        self.data_type = data_type
        self.args = args

        self.top_k = top_k

        self.inputs = []
        self.targets = []
        self.event_descriptions = []

        self._build_examples()

    def __len__(self):
        return len(self.inputs)

    def __getitem__(self, index):
        source_ids = self.inputs[index]["input_ids"].squeeze()
        target_ids = self.targets[index]["input_ids"].squeeze()

        event_description_ids = self.event_descriptions[index]["input_ids"].squeeze()

        src_mask = self.inputs[index]["attention_mask"].squeeze(
        ) 
        target_mask = self.targets[index]["attention_mask"].squeeze(
        )
    
        event_description_mask = self.event_descriptions[index]["attention_mask"].squeeze(
        ) 

        return {
            "source_ids": source_ids,
            "source_mask": src_mask,
            "target_ids": target_ids,
            "target_mask": target_mask,
            "event_description_ids": event_description_ids,
            "event_description_mask": event_description_mask,
        }

    def _build_examples(self):

        if self.args.multi_task:
            inputs, targets = get_transformed_io_unified(
                self.data_path, self.task_name, self.data_name, self.data_type,
                self.top_k, self.args)
        else: 
            inputs, targets, event_descriptions = get_transformed_io(self.data_path,
                                                 self.data_name,
                                                 self.data_type, self.top_k,
                                                 self.args)

        for i in range(len(inputs)):
            input = ' '.join(inputs[i])
            target = targets[i]

            event_description = event_descriptions[i]


            tokenized_input = self.tokenizer.batch_encode_plus(
                [input],
                max_length=self.max_len,
                padding="max_length",
                truncation=True,
                return_tensors="pt")  
            target_max_length = 1024 if self.data_type == "test" else self.max_len

            tokenized_target = self.tokenizer.batch_encode_plus(
                [target],
                max_length=target_max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt")


            tokenized_event_description = self.tokenizer.batch_encode_plus(
                [event_description],
                max_length=100,
                padding="max_length",
                truncation=True,
                return_tensors="pt")  


            self.inputs.append(tokenized_input)
            self.targets.append(tokenized_target)
            self.event_descriptions.append(tokenized_event_description)
