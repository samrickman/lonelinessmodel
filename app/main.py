from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import pandas as pd
import spacy
from constants import default_anon_mask
from create_input_chunks import  create_model_input
from batch_classify import run_classification
from prepare_output import prepare_model_output
from tqdm import tqdm
import re
from pathlib import Path
import os
import json
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "Hello World"}

def get_anon_mask(anon_mask_file):
    if anon_mask_file:
        try:
            logger.info(f"Reading anon_mask_file: {anon_mask_file.filename}")
            anon_mask = json.load(anon_mask_file.file)
            anon_mask_file.file.close()
            logger.info("Anon mask loaded successfully")
        except Exception as e:
            logger.error(f"Error loading anon mask file: {str(e)}", exc_info=True)
            raise HTTPException(status_code=400, detail=f"Error loading anon mask file: {str(e)}")
    else:
        anon_mask = default_anon_mask
        logger.info("Using default anon mask")
    
    return anon_mask


def run_model(df, out_file, anon_mask, overwrite):
    create_out_dir(out_file)    
    text = get_text(df)
    masked = apply_anon_mask(df, text, anon_mask)
    sentences_dict = apply_sentence_tokenization(text_to_split=masked)
    sentence_df = pd.DataFrame(sentences_dict)
    sentence_df.to_csv(out_file, index=False)

    create_model_input(overwrite=overwrite)
    run_classification(overwrite=overwrite)
    model_output = prepare_model_output()

    result = {
        "parameters": {
            "Data frame of sentences written": out_file,
            "PersonID count" : sentence_df['PersonID'].nunique(),
            "DocumentID count" : sentence_df['DocumentID'].nunique(),
            "SentenceID count" : sentence_df['SentenceID'].nunique(),
            "Model input created" : "True",
            "Classification run" : "True",
            "Model output prepared" : "True",
            "anon_mask" : anon_mask
        },
        "predictions" : model_output
    }
    
    logger.info(json.dumps(result))

    return result


@app.post("/upload")
def upload(file: UploadFile = File(...), out_file: str = "./csv_out/sentence_df.csv", anon_mask_file: UploadFile = None, overwrite: str = Form("False")):


    try:
        logger.info("Processing file upload")
        anon_mask = get_anon_mask(anon_mask_file)
        
        try:
            df = pd.read_csv(file.file)
        finally: # make sure file gets closed even if df cannot open
            file.file.close()
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing upload: {str(e)}")
    
    overwrite_bool = overwrite.lower() in ["true", "1", "t", "y", "yes"]
    logger.info(f"""
    Running model with the following parameters:
            df shape: {df.shape},
            out_file: {out_file},
            overwrite: {overwrite},
            overwrite_type : {type(overwrite)},
            overwrite_bool: {overwrite_bool}
    """)
    result = run_model(df, out_file, anon_mask, overwrite_bool)
    logger.info("File processed successfully")
    return result
    

def create_out_dir(out_file):
    print("Creating output directory...")
    out_dir = os.path.dirname(out_file)
    Path(out_dir).mkdir(parents=True, exist_ok=True)

def get_text(df):
    print("Reading in text data...")
    print("Converting all values to string...")
    text = df["response"].apply(lambda x: str(x))
    return text


def apply_anon_mask(df, text, anon_mask):
    print("Applying anonymisation mask...")
    # Purpose of removing punctuation here is to not break
    # json rather than for tokenizing
    punct_to_remove = r'"|\(|\)|\*|\|\[|\\|\]|^|`|{|}'

    # replace with anon-mask
    masked = []
    for i, sample in tqdm(enumerate(text)):
        for phrase in anon_mask.keys():
            if phrase in sample:
                sample = sample.replace(phrase, anon_mask[phrase])

        # Clean punctuation
        sample = sample.replace("\n", " ")
        sample = re.sub(punct_to_remove, "", sample)

        masked.append({
            "PersonID": df['PersonID'][i],
            "date": df['date'][i],
            "DocumentID": df["DocumentID"][i],
            "text": sample
        })

    return masked
    

def create_sentence_dict(note, model):
    doc = model(note['text'])
    sents = list(doc.sents)
    sentence_list = []
    for sentence_index, line in enumerate(sents):
        sentence_id = f"{note['DocumentID']}_{sentence_index}"

        sentence_dict = {
                            "PersonID": note['PersonID'],
                            "date": note['date'],
                            "DocumentID": note["DocumentID"],
                            "SentenceID": sentence_id,
                            "sentence_text": line.text
                        }
        
        sentence_list.append(sentence_dict)
    
    return sentence_list


def apply_sentence_tokenization(
        text_to_split,
        model = "en_core_web_sm",
        disable = ['parser', 'tok2vec', 'tagger', 'attribute_ruler', 'ner', 'lemmatizer'],
        enable = "senter"
    ):
    print("Loading sentence tokenizer...")
    nlp = spacy.load(model, disable=disable)
    nlp.enable_pipe(enable)

    print("Tokenizing sentences...")

    docs = [create_sentence_dict(note, model = nlp) for note in tqdm(text_to_split)]

    docs_flat = [item for sublist in docs for item in sublist]

    return(docs_flat)
