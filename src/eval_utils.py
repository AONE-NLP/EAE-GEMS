import re
import numpy as np
import re
from const import ere_argument_role_list
from const import wikievent_argument_role_list, ere_argument_role_list

def find_all_positions(main_string, substring):
    matches = re.finditer(re.escape(substring), main_string)
    return [match.start() for match in matches]

def find_all_substring_indices(main_string, substrings):
    pattern = re.compile('|'.join(re.escape(substr) for substr in substrings)) 
    matches = pattern.finditer(main_string)
    indices = [(match.group(0), match.start()) for match in matches]
    
    return indices

def find_first_substring_from_position(main_string, substrings, start_position):
    if start_position < 0 or start_position >= len(main_string):
        return None, None
    pattern = re.compile('|'.join(re.escape(substr) for substr in substrings))
    match = pattern.search(main_string, start_position)
    if match:
        matched_substring = match.group(0)
        for substring in substrings:
            if substring == matched_substring:
                return substring, match.start()
    
    return None, None

def extract_spans_para(seq, seq_type):
    quads = []
    sents = [" ".join([s.strip() for s in seq.split('[SSEP]')])]
    elements = [s.strip() for s in seq.split('[SSEP]')] 
    for s in sents: 
        try:
            tok_list = ["[T]", "[A]", "[R]"]

            for tok in tok_list: 
                if tok not in s:
                    s += " {} null".format(tok) 

            index_t = find_all_substring_indices(s, ["[T]"])[0]
            
            index = find_all_substring_indices(s, tok_list) 
            index_a_r = find_all_substring_indices(s, ["[A]", "[R]"])
            index_a = find_all_substring_indices(s, ["[A]"])[:10] 
            index_r = find_all_substring_indices(s, ["[R]"])[:10] 
            index_map = {e: i for i, e in enumerate(index)} 
            
            index_a_map = {e: i for i, e in enumerate(index_a)} 
            index_r_map = {e: i for i, e in enumerate(index_r)} 
            if index_map[index_t] >= 0 and index_map[index_t] < len(index) - 1: 
                next_idx = index[index_map[index_t] + 1][1]
                res_t = s[index_t[1] + 4 : next_idx - 1]
            else: 
                res_t = s[index_t[1] + 4 :]

            res_a_r = []
            if res_t == "null" or res_t == "": 
                res_t = 'null'
                res_a_r.append(("null", "null"))  
            else:

                if index_a_r[0][0] == '[A]':
                    idx_a = 0
                    idx_r = 0
                    while idx_a < len(index_a):
                        cur_a = index_a[idx_a] 
                        if idx_r < len(index_r):
                            cur_r = index_r[idx_r] 
                        else:
                            cur_r = ('null', 1e5)

                        if idx_a < len(index_a) - 1:
                            next_a = index_a[index_a_map[cur_a] + 1]
                            next_a_pos = next_a[1]
                        else:
                            next_a_pos = len(s) - 1
                        if index_map[cur_a] < len(index) - 1:
                            next_ = index[index_map[cur_a] + 1]
                            a = s[cur_a[1] + 4 : next_[1] - 1]
                        else:
                            a = s[cur_a[1] + 4 : ]
                        
                        if cur_r != ('null', 1e5):
                            if index_map[cur_r] < len(index) - 1:
                                next_ = index[index_map[cur_r] + 1]
                                r = s[cur_r[1] + 4 : next_[1] - 1]
                            else:
                                r = s[cur_r[1] + 4 : ]
                        else:
                            r = "null"

                        if cur_r[1] < next_a_pos: 
                            if r == "null" or r == '':  
                                if len(res_a_r) == 0:
                                    res_a_r.append((a, r)) 
                                break   
                            else:
                                res_a_r.append((a, r))
                                idx_a += 1
                                if idx_r < len(index_r):
                                    idx_r += 1
                           
                        else:
                            res_a_r.append((a, "null"))
                            idx_a += 1

                else:

                    idx_a = 0
                    idx_r = 0
                    while idx_a < len(index_a):
                        cur_a = index_a[idx_a] 
                        if idx_r < len(index_r):
                            cur_r = index_r[idx_r] 
                        else:
                            cur_r = ('null', 1e5)
                        
                        if idx_r < len(index_r) - 1:
                            next_r = index_r[index_r_map[cur_r] + 1]
                            next_r_pos = next_r[1]
                        else:
                            next_r_pos = len(s) - 1
                        if index_map[cur_a] < len(index) - 1:
                            next_ = index[index_map[cur_a] + 1]
                            a = s[cur_a[1] + 4 : next_[1] - 1]
                        else:
                            a = s[cur_a[1] + 4 : ]
                        
                        if cur_r != ('null', 1e5):
                            if index_map[cur_r] < len(index) - 1:
                                next_ = index[index_map[cur_r] + 1]
                                r = s[cur_r[1] + 4 : next_[1] - 1]
                            else:
                                r = s[cur_r[1] + 4 : ]
                        else:
                            r = "null"


                        if cur_a[1] < next_r_pos: 
                            if r == "null" or r == '':  
                                if len(res_a_r) == 0:
                                    res_a_r.append((a, r))
                                break   
                            else:
                                res_a_r.append((a, r))
                                idx_a += 1
                                if idx_r < len(index_r):
                                    idx_r += 1
                             
                        else:
                            res_a_r.append((a, ""))
                            idx_a += 1

        except ValueError:
            try:
                print(f'In {seq_type} seq, cannot decode: {s}')
                pass
            except UnicodeEncodeError:
                print(f'In {seq_type} seq, a string cannot be decoded')
                pass
            res_t, res_a_r = '', ['']
        quads.append((res_t, res_a_r))
    
    triplets_result = []

    for q in quads:
        t, a_r_list = q
        for a_r in a_r_list:
            a, r = a_r
            if ("" not in [t, a, r]) and ("null" not in [t, a, r]):
                if r in ere_argument_role_list:  
                    triplets_result.append((t, a, r))

    return triplets_result





def compute_f1_scores(pred_pt, gold_pt, verbose=True):

    arg_pred_pt = [set([g[1] for g in pred_pt[i]]) for i in range(len(pred_pt))]
    arg_gold_pt = [set([g[1] for g in gold_pt[i]]) for i in range(len(gold_pt))]
    arg_n_tp, arg_n_gold, arg_n_pred = 0, 0, 0
    n_tp, n_gold, n_pred = 0, 0, 0

    for i in range(len(pred_pt)):
        n_gold += len(gold_pt[i])
        n_pred += len(pred_pt[i])

        for t in pred_pt[i]:
            if t in gold_pt[i]:
                n_tp += 1

        arg_n_gold += len(arg_gold_pt[i])
        arg_n_pred += len(arg_pred_pt[i])

        for t in arg_pred_pt[i]:
            if t in arg_gold_pt[i]:
                arg_n_tp += 1

    if verbose:
        print(
            f"Arg-Identfication: number of gold spans: {arg_n_gold}, predicted spans: {arg_n_pred}, hit: {arg_n_tp}"
        )
        print(
            f"Arg-Classification: number of gold spans: {n_gold}, predicted spans: {n_pred}, hit: {n_tp}"
        )
    arg_precision = float(arg_n_tp) / float(arg_n_pred) if arg_n_pred != 0 else 0
    arg_recall = float(arg_n_tp) / float(arg_n_gold) if arg_n_gold != 0 else 0
    arg_f1 = 2 * arg_precision * arg_recall / (
        arg_precision + arg_recall) if arg_precision != 0 or arg_recall != 0 else 0
    precision = float(n_tp) / float(n_pred) if n_pred != 0 else 0
    recall = float(n_tp) / float(n_gold) if n_gold != 0 else 0
    f1 = 2 * precision * recall / (
        precision + recall) if precision != 0 or recall != 0 else 0


    scores = {
        'arg_I_prec': arg_precision * 100,
        'arg_I_recall': arg_recall * 100,
        'arg_I_f1': arg_f1 * 100,
        'precision': precision * 100,
        'recall': recall * 100,
        'f1': f1 * 100,
    }

    return scores


def compute_scores(pred_seqs, gold_seqs, verbose=True):

    assert len(pred_seqs) == len(gold_seqs), (len(pred_seqs), len(gold_seqs))
    num_samples = len(gold_seqs)

    all_labels, all_preds = [], []

    for i in range(num_samples): 
        gold_list = extract_spans_para(gold_seqs[i], 'gold')
        pred_list = extract_spans_para(pred_seqs[i], 'pred')

        if verbose and i < 70:

            print("gold seqs ", gold_seqs[i])
            print("gold extr ", gold_list)

            print("pred seqs ", pred_seqs[i])
            print("pred list ", pred_list)
            print()
        all_labels.append(gold_list) 
        all_preds.append(pred_list) 

    scores = compute_f1_scores(all_preds, all_labels)

    return scores, all_labels, all_preds

