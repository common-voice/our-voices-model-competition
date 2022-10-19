# Setting
MODEL_PATH ="./models"
MODEL_NAME = "new_model" # name your new model
BASE_MODEL = "./train/data2vec-thai-pretrained/1" # pretrianed model

import wandb
wandb.login()
wandb.init(project="mozilla", name=MODEL_NAME)

import os
from datasets import load_dataset, load_metric

mixed_train = load_dataset("./cv11_dataloader.py", "th", split="train+validation")
mixed_test = load_dataset("./cv11_dataloader.py", "th", split="test")


import re
from pythainlp.tokenize import word_tokenize

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
    # batch["sentence"] = clean_word(batch["sentence"]).replace(" ", "")
    return batch

mixed_train = mixed_train.map(remove_special_characters).map(clean_batch).map(th_tokenize)
mixed_test = mixed_test.map(remove_special_characters).map(clean_batch).map(th_tokenize)

from transformers import Wav2Vec2Processor

processor = Wav2Vec2Processor.from_pretrained("./train/processor")

import torchaudio

def speech_file_to_array_fn(batch):
    speech_array, sampling_rate = torchaudio.load(batch["path"])
    batch["speech"] = speech_array.numpy()[0]
    batch["sampling_rate"] = sampling_rate
    batch["target_text"] = batch["sentence"]
    return batch

mixed_train = mixed_train.map(speech_file_to_array_fn, remove_columns=mixed_train.column_names)
mixed_test = mixed_test.map(speech_file_to_array_fn, remove_columns=mixed_test.column_names)

import librosa
import numpy as np
import torch

def resample(batch, resample_to=16000):
    if batch["sampling_rate"] != resample_to:
        batch["speech"] = librosa.resample(np.asarray(batch["speech"]), batch["sampling_rate"], resample_to)
        batch["sampling_rate"] = resample_to
    return batch

mixed_train = mixed_train.remove_columns("sampling_rate")
mixed_train = mixed_train.rename_column("speech", "input_values")
mixed_train = mixed_train.rename_column("target_text", "labels")

mixed_test = mixed_test.remove_columns("sampling_rate")
mixed_test = mixed_test.rename_column("speech", "input_values")
mixed_test = mixed_test.rename_column("target_text", "labels")

import torch
import torchaudio
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
# import augment
import sys
sys.path.append("./train/WavAugment") 
import augment

@dataclass
class DataCollatorCTCWithPadding:

    processor: Wav2Vec2Processor
    padding: Union[bool, str] = True
    max_length: Optional[int] = None
    max_length_labels: Optional[int] = None
    pad_to_multiple_of: Optional[int] = None
    pad_to_multiple_of_labels: Optional[int] = None

    def __call__(self, features: List[Dict[str, Union[List[int], torch.Tensor]]]) -> Dict[str, torch.Tensor]:
        # split inputs and labels since they have to be of different lenghts and need
        # different padding methods
        audios = [feature["input_values"] for feature in features]
        sentences = [feature["labels"] for feature in features]

        for i in range(len(audios)):
            audio = audios[i]

            # random change pitch, reverb, time drop
            src_info = {'rate': 16000}

            target_info = {'channels': 1, 
                        'length': 0,
                        'rate': 16000}
            random_pitch = lambda: np.random.randint(-200, 200)
            room_size = np.random.randint(0, 50)
            audio = augment.EffectChain().pitch(random_pitch).channels().rate(16000).apply(torch.Tensor(audio), src_info=src_info, target_info=target_info)
            audio = torch.Tensor(audio)
            audio = self.processor(audio, sampling_rate=16000).input_values
            audio = np.array(audio)
            audio = torch.Tensor(audio).squeeze(0).squeeze(0)
            audios[i] = audio

            with self.processor.as_target_processor():
                sentences[i] = processor(sentences[i]).input_ids

        input_features = [{"input_values": audio} for audio in audios]
        label_features = [{"input_ids": sentence} for sentence in sentences]

        batch = self.processor.pad(
            input_features,
            padding=self.padding,
            max_length=self.max_length,
            pad_to_multiple_of=self.pad_to_multiple_of,
            return_tensors="pt",
        )
        with self.processor.as_target_processor():
            labels_batch = self.processor.pad(
                label_features,
                padding=self.padding,
                max_length=self.max_length_labels,
                pad_to_multiple_of=self.pad_to_multiple_of_labels,
                return_tensors="pt",
            )

        # replace padding with -100 to ignore loss correctly
        labels = labels_batch["input_ids"].masked_fill(labels_batch.attention_mask.ne(1), -100)

        batch["labels"] = labels

        return batch
    
data_collator = DataCollatorCTCWithPadding(processor=processor, padding=True)

cer_metric = load_metric("cer")
wer_metric = load_metric("wer")

def compute_metrics(pred):
    pred_logits = pred.predictions
    pred_ids = np.argmax(pred_logits, axis=-1)

    pred.label_ids[pred.label_ids == -100] = processor.tokenizer.pad_token_id

    pred_str = processor.batch_decode(pred_ids)
    # we do not want to group tokens when computing the metrics
    label_str = processor.batch_decode(pred.label_ids, group_tokens=False)

    wer = wer_metric.compute(predictions=pred_str, references=label_str)
    cer = cer_metric.compute(predictions=pred_str, references=label_str)

    return {"wer": wer, "cer": cer}

from transformers import Data2VecAudioForCTC

# Base model to finetune on top of
model = Data2VecAudioForCTC.from_pretrained(BASE_MODEL, 
                                            attention_dropout=0.1,
                                            hidden_dropout=0.1,
                                            feat_proj_dropout=0.0,
                                            mask_time_prob=0.05,
                                            layerdrop=0.1,
                                            ctc_loss_reduction="mean",
                                            pad_token_id=processor.tokenizer.pad_token_id,
                                            vocab_size=len(processor.tokenizer))

model = model.to("cuda")
model.freeze_feature_extractor()

from transformers import TrainingArguments

training_args = TrainingArguments(
  output_dir=os.path.join(MODEL_PATH, MODEL_NAME),
  group_by_length=True,
  per_device_train_batch_size=16, #8,
  gradient_accumulation_steps=8, #4,
  per_device_eval_batch_size=4,
  evaluation_strategy="steps",
  metric_for_best_model='cer',
  greater_is_better=False,
  num_train_epochs=3000, 
  fp16=True,
  save_strategy="steps",
  save_steps=500, 
  logging_strategy="steps",
  eval_steps=500, 
  logging_steps=500, 
  learning_rate=1e-4, 
  warmup_steps=0,
  save_total_limit=2, 
  dataloader_num_workers=16, 
)

from transformers import Trainer

trainer = Trainer(
    model=model,
    data_collator=data_collator,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=mixed_train,
    eval_dataset=mixed_test,
    tokenizer=processor.feature_extractor
)

trainer.train()