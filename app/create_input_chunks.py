#!/usr/bin/env python
# coding: utf-8



import pandas as pd
import numpy as np
from collections import Counter
import json
import os
from tqdm import tqdm
from fastapi import HTTPException


def split_into_chunked_dict(
        df, 
        cols_to_keep = ["PersonID", "DocumentID", "SentenceID", "sentence_text"],
        chunk_max_size = 100):
    
    df = df[cols_to_keep]
    num_chunks = int(np.ceil(df.shape[0] / chunk_max_size))
    print(f"Breaking into {num_chunks} chunks")
    
    df_chunk_list = np.array_split(df, num_chunks)
    num_rows = [df.shape[0] for df in df_chunk_list]
    row_counts = str(dict(Counter(num_rows)))
    
    print(f"Number of rows per chunk {row_counts}")
    
    chunked_dict_list = [df.to_dict(orient="records") for df in df_chunk_list]
    
    print("File chunked successfully. Saving chunks to disk.")
    
    return chunked_dict_list
    


def save_chunks(chunked_dict_list, outdir = "./chunks_for_model", json_indent = 4):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    for i, chunk in enumerate(tqdm(chunked_dict_list)):
        outfile = f"{outdir}/{i}.json"
        with open(outfile, "w") as f:
            json.dump(chunk, f, indent = json_indent)


def read_csv_input(infile = "./input/all_sentences_2018.csv"):
    if not os.path.exists(infile):
        raise OSError(f"Expecting file: {infile}. File does not exist")
        
    df = pd.read_csv(infile, nrows = 1)
    
    expected_columns = ["PersonID", "DocumentID", "SentenceID", "sentence_text"]
    
    if set(expected_columns).difference(df.columns) != set():
        raise HTTPException(f"Expecting columns to be {expected_columns}")
    
    df = pd.read_csv(infile)
    
    print("File read in successfully")
    return df



def check_outdir_empty(outdir = "./chunks_for_model/", overwrite = False):
    json_files_in_outdir = [file for file in os.listdir(outdir) if file.endswith("json")]

    if json_files_in_outdir != [] and not overwrite:
        raise HTTPException(status_code=400, detail=f"There are already files in the output folder and overwrite is not set to True.")
    for file in json_files_in_outdir:
        os.remove(f"{outdir}{file}")



def remove_na_sentences(df):
    na_sentences = df['sentence_text'].isna()
    num_na = na_sentences.sum()
    if num_na == 0:
        print("No NaN sentences to remove... all OK.")
        return df
    print(f"""
        Removing {num_na} sentences with NaN text prior to classification.
        Were these sentences 'N/A' or 'NA'?
        Snapshot of sentences removed.
        ----------------------------------------------------------------------------------
        {df.iloc[na_sentences.values, :]}
        ----------------------------------------------------------------------------------    
        """
    )
    df = df[~na_sentences.values]
    return df

# Make sure everything left is a string
def coerce_to_string(df):
    not_strings = df['sentence_text'].apply(lambda x: type(x) != str)
    if not_strings.sum() > 0:
        df['sentence_text'] = df['sentence_text'].astype('str')
        
    still_not_strings = df['sentence_text'].apply(lambda x: type(x) != str)
    if still_not_strings.sum() > 0: 
        raise HTTPException(f"""
            Fatal error. Some values could not be converted to string. See below.
            Please remove or fix these sentences before trying again.
            ----------------------------------------------------------------------------------
            {df[still_not_strings]}
            ----------------------------------------------------------------------------------      

        """
        )
    return df

def create_model_input(infile = "./csv_out/sentence_df.csv", outdir = "./chunks_for_model/", overwrite = False):
    check_outdir_empty(outdir, overwrite)
    df = read_csv_input(infile)
    df = remove_na_sentences(df)
    df = coerce_to_string(df)
    chunked_dict_list = split_into_chunked_dict(df)
    save_chunks(chunked_dict_list, outdir)

if __name__ == "__main__":
    create_model_input()





