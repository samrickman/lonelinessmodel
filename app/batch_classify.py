#!/usr/bin/env python
# coding: utf-8

# # Script to batch classify sentences and return json output
# 
# This script takes a json input of sentences (with SentenceID and DocumentID) and returns predictions. 

from datasets import load_dataset
import pandas as pd
import pyarrow as pa
from datasets import Dataset
from transformers import (AutoTokenizer, 
                          AutoModelForSequenceClassification, 
                          Trainer, 
                          TrainingArguments)
import numpy as np
import json
import os


def softmax(x):
    return np.exp(x) / np.sum(np.exp(x), axis=0)

def tokenize_sentences(sentences_to_classify, tokenizer):
    sentences_df = pd.DataFrame(sentences_to_classify, columns = ["PersonID", "DocumentID", "SentenceID", "sentence_text"])
    sentences_ds = Dataset(pa.Table.from_pandas(sentences_df))

    tokenize_func = lambda sentences: tokenizer(sentences['sentence_text'], \
                                                padding="max_length", \
                                                truncation=True)
    tok_sentences_ds = sentences_ds.map(tokenize_func, batched=True)
    
    return tok_sentences_ds

def get_predictions(tokenized_sentences, model):
    trainer = Trainer(model)
    pred = trainer.predict(tokenized_sentences)
    labels = pred.predictions.argmax(axis=1)
    
    
    results = []
    for PersonID, DocumentID, SentenceID, label, proba in zip(
            tokenized_sentences['PersonID'],
            tokenized_sentences['DocumentID'],
            tokenized_sentences['SentenceID'], 
            labels, 
            pred.predictions
        ):
        results_dict = {
            "PersonID"   : PersonID,
            "DocumentID" : DocumentID,
            "SentenceID" : SentenceID,
            "prediction" : int(label), # from int64 - for json 
            # softmax for each result on its own 
            # or the max of all results affects the rest
            "proba" : softmax(proba).tolist() # so serializable 
        }
        results.append(results_dict)
        
    return results




def load_json_chunk(chunk_num, in_dir = "./chunks_for_model/", outdir = "./classified_chunks/"):
    in_file = f"./{in_dir}/{chunk_num}.json"
    with open(in_file, "r") as f:
        sentence_chunk = json.load(f)
        
    if not os.path.exists(outdir):
        os.makedirs(outdir)
        
    return sentence_chunk


def get_max_json_chunk_num(dir_to_check = "./chunks_for_model/", return_start_chunk_num = False):
    files_to_read = [int(file.replace(".json", "")) for file in os.listdir(dir_to_check) if file.endswith("json")]
    
    if not files_to_read:
        return 0

    end_file = max(files_to_read) + 1
    
    return end_file


def classify_chunk(chunk_num, tokenizer, model):
    print(f"Processing chunk: {chunk_num}")
    sentences_to_classify = load_json_chunk(chunk_num)
    print("Tokenizing sentences")
    tokenized_sentences = tokenize_sentences(sentences_to_classify, tokenizer=tokenizer)
    print("Generating predictions")
    predictions = get_predictions(tokenized_sentences, model=model)
    save_classification(predictions, chunk_num)



def save_classification(predictions, chunk_num, json_indent = 4, outdir = "./classified_chunks/"):
        
    outfile = f"{outdir}/{chunk_num}.json"
    with open(outfile, "w") as f:
        json.dump(predictions, f, indent = json_indent)

def write_error_log(chunk_num, error_msg, outdir = "./classified_chunks/", errors_dir = "./errors/"):

    # write empty json so it can move on to next chunk
    outfile = f"{outdir}/{chunk_num}.json"
    with open(outfile, 'a'):
        os.utime(outfile, None)

    # Add chunk_num to error log
    if not os.path.exists(errors_dir):
        os.makedirs(errors_dir)
    
    # Log just the chunk number
    with open(f"{errors_dir}/chunk_num.log", 'a+') as f:
        f.write(f"{chunk_num}\n")

    # Log the actual exception as well
    LINE_WIDTH = 80
    with open(f"{errors_dir}/exception_details.log", 'a+') as f:
        f.write(f"{chunk_num}:\n")
        f.write(f"    {error_msg}\n")
        f.write(f"{'-' * LINE_WIDTH}\n\n\n")
        


def load_model():
    tokenizer = AutoTokenizer.from_pretrained("roberta-base")
    model = AutoModelForSequenceClassification.from_pretrained("./model", local_files_only=True)
    return tokenizer, model



def run_classification(print_progress_every_n = 100, overwrite = False):
    tokenizer, model = load_model()
    # Start classifying from first file not classified unless overwriting
    if overwrite:
        start_chunk = 0
    else:
        start_chunk = get_max_json_chunk_num("./classified_chunks/", return_start_chunk_num=True)
    end_chunk = get_max_json_chunk_num("./chunks_for_model/")
    print(f"Start chunk: {start_chunk}\nEnd chunk: {end_chunk}")
    if start_chunk == end_chunk:
        input("All chunks have already been classified. Press Enter to exit.")
        exit(0)
    
    for chunk_num in range(start_chunk, end_chunk):
        try:
            classify_chunk(chunk_num, tokenizer, model)
        except Exception as e:
            write_error_log(chunk_num, e)
        

            

if __name__ == "__main__":
    run_classification()