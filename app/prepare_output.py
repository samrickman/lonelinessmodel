#!/usr/bin/env python
# coding: utf-8

import numpy as np
import json
import os
from tqdm import tqdm
import pandas as pd



def get_chunk_list(in_dir = "./classified_chunks/", ext = "json"):
    chunk_list = [f"{in_dir}{file}" for file in os.listdir(in_dir) if file.endswith(ext)]
    return chunk_list


def read_chunk(chunk_path):
    try:
        with open(chunk_path, "r") as f:
            chunk = json.load(f)
        return chunk
    except:
        return None


def partition_chunk(chunk):
    negatives = []
    positives = []
    for sentence in chunk:

        if not sentence['prediction'] in [0,1]:
            raise Exception(f"""
            This chunk has an incorrect classification (must be 0 or 1). 
            PersonID: {sentence['PersonID']}
            DocumentID: {sentence['DocumentID']}    
            SentenceID: {sentence['SentenceID']}
            """)   

        if sentence['prediction'] == 0:
            negatives.append(sentence)

        if sentence['prediction'] == 1:
            positives.append(sentence)        

    return positives, negatives



def flatten(l):
    return [item for sublist in l for item in sublist]



def partition_all_chunks(chunk_list):
    
    all_positives = []
    all_negatives = []
    all_problems = []
    for chunk_file in tqdm(chunk_list):
        chunk = read_chunk(chunk_file)
        
        # If file can't be read
        # we've already printed a message
        if chunk is None:
            all_problems.append(chunk_file)
            continue
        
        positives, negatives = partition_chunk(chunk)
        all_positives.append(positives)
        all_negatives.append(negatives)

    all_positives = flatten(all_positives)
    all_negatives = flatten(all_negatives)

    print(f"Problems reading {len(all_problems)} files.")
    
    return all_positives, all_negatives, all_problems


def get_preds():
    chunk_list = get_chunk_list()
    all_positives, all_negatives, all_problems = partition_all_chunks(chunk_list)
    positive_preds = pd.DataFrame(all_positives)
    negative_preds = pd.DataFrame(all_negatives)
    all_preds = pd.concat([positive_preds, negative_preds])
    all_preds['proba_0'] = all_preds.proba.apply(lambda x: x[0])
    all_preds['proba_1'] = all_preds.proba.apply(lambda x: x[1])
    all_preds.drop(columns = 'proba', inplace = True)
    return all_preds


def join_preds_with_text(preds, sentence_file = "./csv_out/sentence_df.csv"):
    sentences = pd.read_csv(sentence_file)
    sentences_preds = sentences.merge(preds, on = ['PersonID', 'DocumentID', 'SentenceID'], how = 'left')
    return sentences_preds

def prepare_model_output(out_file_json = "./csv_out/classified_sentences.json"):
    preds = get_preds()
    sentences_preds_df = join_preds_with_text(preds)
    out_dict = sentences_preds_df.to_dict(orient="records")
    out_json = json.dumps(out_dict, indent=4)
    # Save it in case it being returned gets lost somehow
    with open(out_file_json, "w") as f:
        f.write(out_json)
    print(f"JSON written to {out_file_json}")
    return out_dict


if __name__ == "__main__":
    prepare_model_output()

