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

# def remove_special_characters(batch):
#     return re.sub(chars_to_ignore_regex, '', batch).lower()

# def th_tokenize(batch):
#     token_str = " ".join(word_tokenize(batch, engine="newmm"))
#     return ' '.join(token_str.split())

# def clean_word(word):
#     i = 0
#     word_result = ""
#     while i < len(word):
#         if word[i] == "ํ" and word[i+1] == "า":
#             word_result += "ำ"
#             i += 2
#         if word[i] == "เ" and word[i+1] == "เ":
#             word_result += "แ"
#             i += 2
#         else:
#             word_result += word[i]
#             i += 1
#     return word_result

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
    # batch["sentence"] = clean_word(batch["sentence"]).replace(" ", "")
    return batch

# def clean_word(word):
#     i = 0
#     word_result = ""
#     while i < len(word):
#         if word[i] == "ํ" and word[i + 1] == "า":
#             word_result += "ำ"
#             i += 2
#         else:
#             word_result += word[i]
#             i += 1
#     return word_result

class Torch_Speech_Service:
    def __init__(self, model_path, lm_path, device="cpu"):
        # load pretrained processor and model
        print("Initializing model ...")
        self.processor = Wav2Vec2Processor.from_pretrained(
            "/home/kongpolc/asr/models/cv7/processor" ####
        )

        # Choose Model
        original = Data2VecAudioForCTC.from_pretrained(model_path)
        # original = Wav2Vec2ForCTC.from_pretrained(model_path)

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
            # result = " ".join(self.processor.tokenizer.convert_ids_to_tokens(predicted_ids[0].tolist())) ####
            # print(" ".join(self.processor.tokenizer.convert_ids_to_tokens(predicted_ids[0].tolist()))) ####
            result = self.processor.batch_decode(predicted_ids)

        return result

class PredictFactory():
    def __init__(self, speech_service):
        self.speech_service = speech_service
    
    def get_predict_func(self, do_postprocess=True):

        def predict(path):
            # try:
            #path =path.replace('clips','clips_wav')
            path =path.replace('mp3','wav')
            print(path)
            predict = self.speech_service.predict(audio_file=path, do_postprocess=do_postprocess)[0] #.replace(" ","") ####
            # # except:
            #     print('\n---- Prediction error ----\n', path)
            #     return ''
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
    genders = list(cv7_test_pd.gender)
    # print('\n\n------Listed Ref------\n', clean_references)
    cer_result = cer.compute(predictions=predicts, references=clean_references)
    
    # clean_references = [word_tokenize(data, engine=tokenize_engine) for data in clean_references]
    # clean_references = [" ".join(data) for data in clean_references]
    # predicts = [word_tokenize(data, engine=tokenize_engine) for data in predicts]
    # predicts = [" ".join(data) for data in predicts]
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
model_path = "/home/nattanaa/ASR_train/data2vec_finetune_common11_balance_3_added/checkpoint-29500" #"models/data2vec-thai-finetuned/2.6.2_techsauce_knowledges_sad_on_top_th/checkpoint-10500" #"models/data2vec-thai-finetuned/2.7.1_amz_bilingual/checkpoint-7500" #"models/data2vec-thai-finetuned/2.4.1_all_except_wang/checkpoint-37500" #"models/data2vec-thai-finetuned/2.6.1_techsauce_knowledges_sad_on_top/checkpoint-8500" #"models/data2vec-thai-finetuned/2.6_techsauce_knowledges_sad_on_top/checkpoint-19000" #"models/data2vec-thai-finetuned/1/checkpoint-18000"
# # wav2vec2
# model_path = "/home/kongpolc/asr/models/wav2vec2-finetuned/4/WEDO_mixed_2_cp8000"

lm_name = "/home/kongpolc/asr/models/newmm_4gram.bin" #"WEDO_common_tech_sad_scg_wedo.bin"
lm_path = os.path.join("models", lm_name) #"models/newmm_4gram.bin" # "models/WEDO_common_tech.bin"

speech_service = Torch_Speech_Service(model_path, lm_path, "cuda")

# cv7_test_paths = [
#                   "../data/smart_home/en-th/techsauce_demo/test2.csv",
#                   "../data/company_knowledge/scg_knowledge/test2.csv",
#                   "../data/company_knowledge/wedo_knowledge/test2.csv",
#                  "../data/sad_intent/test_normal_2.csv",
#                  # "../data/nlp_pilot_clean/test_3_cleaned_with_source.csv",
#                  "../data/cv-corpus-9.0-2022-04-27-16000Hz/th/cv9_diff_test_cleaned_wav.csv",
#                  # "../data/smart_home/en-th/amazon_massive_th/test2_bilingual.csv",
#                  "../data/roojai_line/roojai_line.csv"
#                  ]

#audio_paths = [
#              "/home/shared/commonvoice11/data/clips_wav"]
#               "../data/company_knowledge/scg_knowledge/clips",
#               "../data/company_knowledge/wedo_knowledge/clips",
#               "../data/sad_intent/clips",
#               # "../data/nlp_pilot_clean/STT-Pilot-Dataset/pilot-voice-data/wav",
#               "../data/cv-corpus-9.0-2022-04-27-16000Hz/th/clips",
#               # "../data/smart_home/en-th/amazon_massive_th/clips",
#               "../data/roojai_line/clips"
#               ]

# TH 
#df_dev= pd.read_csv("/home/nattanaa/ASR_gender/dev_cleaned.tsv",sep='\t')
#df_test= pd.read_csv("/home/nattanaa/ASR_gender/test_cleaned.tsv",sep='\t')
#df_train= pd.read_csv("/home/nattanaa/ASR_gender/train_cleaned.tsv",sep='\t')
#df_common11=pd.concat([df_dev, df_test,df_train], ignore_index=True)
#df_common11_val_clean=pd.read_csv("/home/shared/commonvoice11/annotation/regular_split/validated_cleaned.tsv",sep='\t')

# converting df file into csv
# df_common11_val_clean.to_csv('common11_full.csv',index=False)

cv7_test_paths = [
                  "/home/nattanaa/ASR_train/mozilla/normal/normal_test.csv"
                 ]

audio_paths = [
              "/home/shared/commonvoice11/data/clips_wav"
              ]

for i in range(len(cv7_test_paths)):
    if not os.path.exists(cv7_test_paths[i]):
        raise FileNotFoundError(f"[Errno 1] No such file or directory: '{cv7_test_paths[i]}'")
    if not os.path.exists(audio_paths[i]):
         raise FileNotFoundError(f"[Errno 2] No such file or directory: '{audio_paths[i]}'")


# Evaluation
eval_report = ''
for i in range(len(cv7_test_paths)):
    cv7_test_path = cv7_test_paths[i] #"../data/company_knowledge/scg_knowledge/test2.csv" #"../data/smart_home/en-th/techsauce_demo/test2.csv" #"../data/sad_intent/test_normal.csv"
    if cv7_test_path.split('.')[-1] == 'tsv':
        cv7_test_pd = pd.read_csv(cv7_test_path, sep='\t')
    else:
        cv7_test_pd = pd.read_csv(cv7_test_path)

    audio_path = audio_paths[i] #"../data/company_knowledge/scg_knowledge/clips" #'../data/smart_home/en-th/techsauce_demo/clips' #"../data/sad_intent/clips"

    paths = cv7_test_pd.path
    references = cv7_test_pd.sentence
    paths = [os.path.join(audio_path, p) for p in paths]

    # Predict and Evaluate - LM
    df, cer_result, wer_result, wer_results, cer_results, predicts, clean_references = evaluate(paths, cv7_test_pd, speech_service, do_postprocess=True, tokenize_engine="newmm", num_workers=NUM_WORKERS)
    
    # Compare word error
    df['word_diff'] = df.apply(lambda x: compare(x['sentence'], x['prediction']) if(x['wer'] > 0.) else None, axis=1)

    dataset = cv7_test_path.split('/')[-2]
    df.to_csv('/home/nattanaa/eval/balanced_3_train/common11_evaluation_normal_3added.csv')
    # with open(os.path.join(model_path, str(dataset)+'_'+'evaluation.txt'), 'w') as file:
    #     file.write(f'WER: {wer_result:.4f}\nCER: {cer_result:.4f}')
    
    report = f"======== {dataset} with LM ({lm_name.split('.')[0]}) =======\nWER: {wer_result:.4f}\nCER: {cer_result:.4f}\n"
    print(report) 
    eval_report += report

#     # Predict and Evaluate - No LM
#     df, cer_result, wer_result, wer_results, cer_results, predicts, clean_references = evaluate(paths, cv7_test_pd, speech_service, do_postprocess=False, tokenize_engine="newmm", num_workers=NUM_WORKERS)

#     # Compare word error
#     df['word_diff'] = df.apply(lambda x: compare(x['sentence'], x['prediction']) if(x['wer'] > 0.) else None, axis=1)

#     dataset = cv7_test_path.split('/')[-2]
#     df.to_csv(os.path.join(model_path, str(dataset)+'_'+'evaluation_no_lm.csv'), index=False)
#     # with open(os.path.join(model_path, str(dataset)+'_'+'evaluation_no_lm.txt'), 'w') as file:
#     #     file.write(f'WER: {wer_result:.4f}\nCER: {cer_result:.4f}')
        
#     report = f'======== {dataset} with No LM =======\nWER: {wer_result:.4f}\nCER: {cer_result:.4f}\n\n'
#     print(report)
#     eval_report += report
report_path = "/home/nattanaa/eval/balanced_3_train/evaluation_report_normal_3added.txt"    
now = datetime.now().strftime('%Y%m%d_%H%M')
# eval_report_path = os.path.join(report_path)
with open(report_path, 'w') as file:
    file.write(eval_report)