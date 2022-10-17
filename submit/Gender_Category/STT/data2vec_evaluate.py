import pandas as pd
import numpy as np
import re
import transformers
from multiprocessing.pool import ThreadPool

from tqdm import tqdm
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torchaudio
import torch
import kenlm
from pyctcdecode import build_ctcdecoder

from datasets import load_metric
from pythainlp.tokenize import word_tokenize 

cer = load_metric("cer")
wer = load_metric("wer")

import os

import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torchaudio
import torch
import kenlm
from pyctcdecode import build_ctcdecoder
import pandas as pd

from multiprocessing.pool import ThreadPool
from transformers import Data2VecAudioForCTC

from datetime import datetime

chars_to_ignore_regex = '[\,\?\.\!\-\;\:\"\“\%\‘\”\�\’\']'

def remove_special_characters(batch):
    batch["sentence"] = re.sub(chars_to_ignore_regex, '', batch["sentence"]).lower()
    return batch

def th_tokenize(batch):
    # batch["sentence"] = " ".join(word_tokenize(batch["sentence"], engine="newmm"))
    batch["sentence"] = " ".join(word_tokenize(batch["sentence"], engine="newmm"))
    batch["sentence"] = ' '.join(batch["sentence"].split())
    return batch

def clean_word(word):
    i = 0
    word_result = ""
    while i < len(word):
        if word[i] == "ํ" and word[i+1] == "า":
            word_result += "ำ"
            i += 2
        if word[i] == "เ" and word[i+1] == "เ":
            word_result += "แ"
            i += 2
        else:
            word_result += word[i]
            i += 1
    return word_result

def clean_batch(batch):
    batch["sentence"] = clean_word(batch["sentence"])
    return batch



class Torch_Speech_Service:
    def __init__(self, model_path, lm_path, device="cpu"):
        # load pretrained processor and model
        print("Initializing model ...")
        self.processor = Wav2Vec2Processor.from_pretrained(
            "./processor" ####
        )

        # Choose Model
        original = Data2VecAudioForCTC.from_pretrained(model_path)

        self.model = original.eval()
        self.device = torch.device(device)
        self.model = self.model.to(self.device)

        self.lm = kenlm.Model(lm_path)
        vocab_dict = self.processor.tokenizer.get_vocab()
        sort_vocab = sorted((value, key) for (key, value) in vocab_dict.items())
        self.vocab = [
            x[1].replace("|", " ")
            if x[1] not in self.processor.tokenizer.all_special_tokens
            else ""
            for x in sort_vocab
        ]
        self.lm_decoder = build_ctcdecoder(
            self.vocab, self.lm, alpha=0.5, beta=2.0
        )
        self.resampling_to = 16000

    def predict(self, audio_file, do_postprocess=True):
        # preprocess
        speech_array, sampling_rate = torchaudio.load(audio_file)
        resampler = torchaudio.transforms.Resample(sampling_rate, self.resampling_to)
        audio_Test = resampler(speech_array)[0]

        inputs = self.processor(
            audio_Test,
            sampling_rate=self.resampling_to,
            return_tensors="pt",
            padding=True,
        )

        inputs = inputs.to(self.device)

        # inference
        with torch.no_grad():
            logits = self.model(
                inputs.input_values,
            )[0]

        result = None

        # post process
        if do_postprocess:
            # KenLM Decoded prediction
            lm_logits = logits.cpu().detach().numpy()[0]
            result = [self.lm_decoder.decode(lm_logits, beam_width=500)]
        else:
            predicted_ids = torch.argmax(logits, dim=-1)
            result = self.processor.batch_decode(predicted_ids)

        return result

class PredictFactory():
    def __init__(self, speech_service):
        self.speech_service = speech_service
    
    def get_predict_func(self, do_postprocess=True):

        def predict(path):
            path =path.replace('mp3','wav')
            print(path)
            predict = self.speech_service.predict(audio_file=path, do_postprocess=do_postprocess)[0] 
            try:
                predict = clean_word(predict)
            except:
                print('\n---- Prediction cannot be cleaned ----\n', predict)
            return predict
        

        return predict

def evaluate(paths, references, speech_service, do_postprocess=True, tokenize_engine="newmm", num_workers=4):
    pred_fac = PredictFactory(speech_service)
    predict_func = pred_fac.get_predict_func(do_postprocess)

    # Predict
    with ThreadPool(num_workers) as pool:
        predicts = list(tqdm(pool.imap(predict_func, paths), total=len(paths)))
        print(predicts)
    # print('\n\n------Predictions------\n', predicts)
    
    # Evaluate
    # clean_references = [data.replace(" ", "") for data in references]
    clean_references = references.apply(remove_special_characters, axis=1)
    clean_references = clean_references.apply(clean_batch, axis=1)
    clean_references = clean_references.apply(th_tokenize, axis=1)
    # print('\n\n------Ref------\n', clean_references)
    clean_references = list(clean_references['sentence'])
    genders = list(cv11_test_pd.gender)
    # print('\n\n------Listed Ref------\n', clean_references)
    cer_result = cer.compute(predictions=predicts, references=clean_references)
    wer_result = wer.compute(predictions=predicts, references=clean_references)
    
    wer_results = []
    cer_results = []
    #normalize token word
    for i in range(len(predicts)):
        predicts[i]=predicts[i].replace(" ", "")

    for i in range(len(clean_references)):
        clean_references[i]=clean_references[i].replace(" ", "")

    predicts = [word_tokenize(data, engine="newmm") for data in predicts]
    predicts = [" ".join(data) for data in predicts]
    clean_references = [word_tokenize(data, engine="newmm") for data in clean_references]
    clean_references = [" ".join(data) for data in clean_references]

    for i in range(len(predicts)):
        wer_results.append(round(wer.compute(predictions=[predicts[i]], references=[clean_references[i]]), 4))
        cer_results.append(round(cer.compute(predictions=[predicts[i]], references=[clean_references[i]]), 4))
    
    # return cer_result, wer_result, predicts, clean_references
    
    df = pd.DataFrame({'path': paths,
                       'sentence': clean_references,
                       'prediction': predicts,
                       'wer': wer_results,
                       'cer': cer_results,
                       'gender': genders})

    return df, cer_result, wer_result, wer_results, cer_results, predicts, clean_references

def compare(label, pred):
    ''' Compare word error '''
    label_words = label.split(' ')
    pred_words = pred.split(' ')
    
    label_diff = []
    pred_diff = []
    for word in label_words:
        if word not in pred_words:
            label_diff.append(word)
    for word in pred_words:
        if word not in label_words:
            pred_diff.append(word)
            
    return label_diff, pred_diff

# Settings
NUM_WORKERS = 4
# data2vec
model_path = <MODEL_PATH>
lm_path = "./newmm_4gram.bin"


speech_service = Torch_Speech_Service(model_path, lm_path, "cuda")

cv11_test_paths = [
                  "./test.csv"
                 ]

audio_paths = [
              "./Methods_and_Measures/commonvoice11/data/clips_wav"
              ]

for i in range(len(cv11_test_paths)):
    if not os.path.exists(cv11_test_paths[i]):
        raise FileNotFoundError(f"[Errno 1] No such file or directory: '{cv11_test_paths[i]}'")
    if not os.path.exists(audio_paths[i]):
         raise FileNotFoundError(f"[Errno 2] No such file or directory: '{audio_paths[i]}'")


# Evaluation
eval_report = ''
for i in range(len(cv11_test_paths)):
    cv11_test_path = cv11_test_paths[i]
    if cv11_test_path.split('.')[-1] == 'tsv':
        cv11_test_pd = pd.read_csv(cv11_test_path, sep='\t')
    else:
        cv11_test_pd = pd.read_csv(cv11_test_path)

    audio_path = audio_paths[i] 
    paths = cv11_test_pd.path
    references = cv11_test_pd.sentence
    paths = [os.path.join(audio_path, p) for p in paths]

    # Predict and Evaluate - LM
    df, cer_result, wer_result, wer_results, cer_results, predicts, clean_references = evaluate(paths, cv11_test_pd, speech_service, do_postprocess=True, tokenize_engine="newmm", num_workers=NUM_WORKERS)
    
    # Compare word error
    df['word_diff'] = df.apply(lambda x: compare(x['sentence'], x['prediction']) if(x['wer'] > 0.) else None, axis=1)

    dataset = cv11_test_path.split('/')[-2]
    df.to_csv('./result.csv')
   
    
    