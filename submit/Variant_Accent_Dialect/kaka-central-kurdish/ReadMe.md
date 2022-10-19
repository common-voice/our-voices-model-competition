
  

# Central Kurdish STT Project

  

## Submission for Our voices competition

  

  

Kurdish language has two major dialects, Sorani (Central Kurdish) and Kurmanji (Northern Kurdish), both of which lack a STT solution primarily because they lack a voice corpus. This, however, has changed alot thanks to the Common Voice project. Now with the latest 11th release of this corpus we have access to 100+ hours for Sorani and 50+ hours for Kurmanji. This is the model I built for this competition.

### Category 
<!--  choose the checkboxes most relevant to your request by filling out the checkboxes with [x] here -->

- [ ] Gender 

- [x] Variant Dialect or Accent

- [ ] Methods and Measures 

- [ ] Open
### Band 
<!--  choose the checkboxes most relevant to your request by filling out the checkboxes with [x] here -->

- [ ]  Band A consists of languages with a corpus of 750 sentences or fewer.
- [x]  Band B consists of languages with a corpus of between 751 and 2,000 sentences.
- [ ]  Band C consists of languages with a corpus of more than 2,001 sentences.
# TLDR;🤌

  

- Small and efficient, 140MB checkpoint, 70MB when converted to ONNX or Nemo format and 20MB when quantized dynamically if some speed loss is acceptable.

- Faster than realtime on CPU, 11x on i3-6100 🔥

- Python-ready, C# Windows port and Word addin with live transcription on its way

- Uses all ckb validated.tsv files (80/20%) data splits

- Validation WER
  | Epoch | WER | Artifact version | Download checkpoint |
  |---|---|---|---|
  | 311 | 0.0703 |73|[Get from releases](https://github.com/dkakaie/our-voices-model-competition/releases/tag/v0.1)|
  | 320 | 0.0678 |75|To be released|

- Results on [Asosoft speech corpus](https://github.com/AsoSoft/AsoSoft-Speech-Corpus) at ***epoch 311***. Alpha and Beta parameters for LM were tuned using [Optuna](https://github.com/optuna/optuna) for 1000 runs each.

  |Decoder|Metric|LM|Distance|Alpha|Beta|
  |---|---|---|---|---|---|
  |**CTCLM**|**WER**|**rudaw-words.binary**|**0.3043**|**0.6785698739930361**|**7.450340924842905**|
  |CTCLM|WER|aso-large-char.binary|0.3478|-0.8143531604631804|-2.199446473162692|
  |Greedy|WER|N/A|0.3567|N/A|N/A|
  |**CTCLM**|**CER**|**rudaw-words.binary**|**0.0533**|**0.6989895457688899**|**8.039499602634686**|
  |Greedy|CER|N/A|0.0652|N/A|N/A|
  |CTCLM|CER|aso-large-char.binary|0.0666|-0.22963118710288732|-8.518252714852693|

# Building blocks

  

- [NeMo](https://github.com/NVIDIA/NeMo)

- [Quartznet](https://arxiv.org/abs/1910.10261) network

- Finetuned a [pretrained English Quartznet model](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/stt_es_quartznet15x5) by Nvidia on CV11 Central Kurdish

- All validated.tsv files have been used. first 80% of files used for train and the remaining 20% for validation. Download my splits from releases [here](https://github.com/dkakaie/our-voices-model-competition) or prepare yours.

- Unfortunately CV8-11 contains non standard Kurdish text which needed to be corrected prior to training. The most problematic one being U+06D5 instead of U+0647. To this end I have used [Asosoft library](https://github.com/AsoSoft/AsoSoft-Library) to normalize the sentences. [Abdulhadi](https://github.com/hadihaji) provided some tricks which seem to have corrected almost all errors. (Thanks!)

- Asosoft has released [a subset of their internal dataset](https://github.com/AsoSoft/AsoSoft-Speech-Corpus) for public use. I have tested the final model on this.

- Decoding with language model is also supported. In this submission [pyctcdecode](https://github.com/kensho-technologies/pyctcdecode) is used, please refer to the corresponding project for more information.

- Checkout Wandb training [report](https://wandb.ai/greenbase/ASR-CV-Competition/reports/Central-Kurdish-STT--VmlldzoyODEwNjYz?accessToken=f8u7n16uf58an1th0jlbedunwst36vltqkjtwqecgr4h2i09hu3jy1i1ej6q2hyb).

- Download ready-to-use epoch 311 model from releases [here](https://github.com/dkakaie/our-voices-model-competition/releases/tag/v0.1) or the best performing one from Wandb. You'll have to convert the checkpoint to nemo before inference or change inference code to load from checkpoint instead of nemo model. KenLM models I used are also available there.

- LM boosting results using two KenLM models are provided. A char KenLM model I trained on [Asosoft text corpus large version](https://github.com/AsoSoft/AsoSoft-Text-Corpus) weighting 31MB and one prepared for news articles from Rudaw. Both models are o=5.

- Training was done using a single RTX 3090 (batch size=64) for about 2 days and still ongoing.

- Kurdish is phonetically consistent. This might have helped the network learn faster. Given the results and small dataset used, this can be a good starting point for future Kurdish STT work.

  

# How to

## Train

Change what you need to change in quartznet_15x5.yaml (datasets, learning rate, etc) and run

    python finetune-quartznet.py

Be sure to login to Wandb before running to keep track of your training progress

## Run inference
First convert your checkpoint to Nemo model format:

    python convert_checkpoint_to_nemo.py {checkpoint_name} {out_model.nemo}
then

    python infer.py --model {out_model.nemo} [List of files to transcribe]
You'll get a prettytable with results.
