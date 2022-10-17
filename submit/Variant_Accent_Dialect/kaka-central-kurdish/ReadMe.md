
# Central Kurdish STT Project

## Submission for Our voices competition

  

Kurdish language has two major dialects, Sorani (Central Kurdish) and Kurmanji (Northern Kurdish), both of which lack a STT solution primarily because they lack a voice corpus. This, however, has changed alot thanks to the Common Voice project. Now with the latest 11th release of this corpus we have access to 100+ hours for Sorani and 50+ hours for Kurmanji. This is the model I built for this competition.

  
# TLDR;🤌

 - Small and efficient, 140MB checkpoint, 70MB when converted to ONNX.
 - Faster than realtime on CPU 🔥
 - Python-ready, C# Windows port and Word addin with live transcription on its way
 - Results on [Asosoft corpus](https://github.com/AsoSoft/AsoSoft-Speech-Corpus) (4.30hours Sorani speech, 7 males, 1 female)

| Decoder | WER |
|--|--|
| greedy | 0.0 |
| kenlm| 0.0 |


# Building blocks

 - [NeMo](https://github.com/NVIDIA/NeMo)
 - [Quartznet](https://arxiv.org/abs/1910.10261) network
 - Finetuned a [pretrained English model](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/nemo/models/stt_es_quartznet15x5) by Nvidia on CV11 Central Kurdish
 - All validated.tsv files have been used. first 80% of files used for train and the remaining 20% for test.
 - Unfortunately CV8-11 contains non standard Kurdish text which needed to be corrected prior to training. To this end I have used [Asosoft library](https://github.com/AsoSoft/AsoSoft-Library) to normalize the sentences. Abdulhadi Riwandizi provided some tricks which seem to have corrected almost all errors. (Thanks!)
 - Both train and test splits I used are provided.
 - Asosoft has released [a subset of their internal dataset](https://github.com/AsoSoft/AsoSoft-Speech-Corpus) for public use. I have tested the final model on this.
 - The python version lacks LM based decoding. However a .NET version of the software has been developed which employs a very small KenLM model leading to lower WER.
 - Training logs are available on Wandb.
 - Download pretrained checkpoints from here
 - LM boosting uses a char KenLM model I trained on [Asosoft text corpus](https://github.com/AsoSoft/AsoSoft-Text-Corpus) (o=5) weighting 31MB.
 - Training was done using a single RTX 3090 for about 12 hours. (batch size=64)
 - Kurdish is phonetically consistent. This might have helped the network learn faster. Given the results and small dataset used, this can be a good starting point for future Kurdish STT work. 
