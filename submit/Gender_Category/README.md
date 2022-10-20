# Gender: A Speech-to-Text Model for Thai

## Introduction
WEDO's mission is to create sustainable and purposeful innovations using voice technology that is more fair and more open to everyone. We have developed our own voice command system and embedded it into smart home appliances, such as speakers and faucets, for better living. In addition, we are building “a voice-enabled device equipped with a camera for blind people” to guide them directions while walking on a street. Thanks to Mozilla Common Voice and its open-source datasets, we are able to build incredible things that have a positive impact on people's lives. This motivates us to build a speech to text (STT) model with gender inclusive performance. More precisely, our STT model should perform equally well for both male and female.

First, we explored the Common Voice 11 dataset. It seemed that there was gender bias. Total data are 135,897 files, which are composed of 52,769 files for male, 30,283 files for female, 1,821 files of other gender, and  51,024 files for undefined gender. This meant that female data was about one-third smaller than male data. As a result, if the model trained with the male-dominant data, the model tended to be biased to male voices. Thus, we tried to find ways to build the gender-inclusive model. However, the experiments showed that our models were not biased toward male voices. In fact, we can recognize female voices slightly better than male voices in most cases of our experiments.

Our contributions can be summarized as follows.

1. We perform an exploratory data analysis to understand data bias over gender in the Common Voice 11 dataset.
2. We propose a STT for Thai, which is fine-tuned on Data2Vec, a state-of-the-art for self-supervised learning in speech.
3. We conduct an experiment to understand performance bias possibly caused by data bias in the Common Voice 11 dataset.
4. To augment Common Voice 11 data, we propose a gender classification model that can infer a gender with F1-score of 0.95.
5. Finally, we did a further analysis to validate various assumptions about performance bias due to data bias between male and female.

## Prerequisites
In this project, we trained models and conducted experiments using a Linux server with GPU. The specification of our computer is listed below:
* CPU:
    * AMD Ryzen7 5800X 3.8GHz
    * RAM: 32GB x 2

* GPU:
    * NVIDIA RTX A6000 48GB

## Project Outline 
To evaluate our project, please perform each step in the following order:

1. Understand the overall study
  * open the notebook "main.ipynb"
  * You expected to see 1. Dataset analysis based on gender distribution 2. Dataset preparation for ASR model training 3. Model performance evaluation of STT model and Gender classifier which reported in WER and CER for STT and accuracy for gender classifier.
  
2. Reproduce our STT model
  * To reproduce our STT model please visit `./STT`. Inside this directory, you can find the `README.md` file containing the steps to reproduce the STT model.

3. Reproduce our gender classification model
  * To reproduce our gender classifier please visit `./gender_classification`. Inside this directory, you can find the `README.md` file containing the steps to reproduce the STT model.

Please noted that to reproduce our work, it is required to download and preprocess datasets. Visit `./data/scripts/`. Run `load_commonvoice11.sh` to download Commonvoice11 dataset and `load_thai_ser.sh` to download Thai-SER dataset.
 

