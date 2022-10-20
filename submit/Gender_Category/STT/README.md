## STT finetune 
 
Thank you for visiting our work to access our STT model. There are 2 options for you.
 - First, if you want to reproduce our work, just follow the Setup and Model Training section to retrain the base model.
 - Second, for those who just want to evaluate our trained models, you can simply download models and follow the evaluation part to get the result.csv file.

### Setup

```
pip install -r requirements.txt
```

Then, download the following files or run this script to automatically download the essential files for model training.
```
bash ./setup.sh
``` 

- <a href="https://drive.google.com/drive/folders/1zM_yEi0eEiAItiVSIlQeSgIGderRemHu?usp=sharing">Pretrained model</a>
- <a href="https://drive.google.com/drive/folders/1bsj7DV6Y9hYf4C-Tx0P6tmvPr2hJtwsp?usp=sharing">Processor</a>
- <a href="https://drive.google.com/file/d/1TX-Fp9CWz7U2AicAjhy3gmDoM7XHqSty/view?usp=sharing">Language Model</a>
- <a href="https://drive.google.com/drive/folders/1LAkmsgQ1KrxuFO54UOTnrA7NWcOGAshX?usp=sharing">WavAugment</a>







### Model training
Our base model is Data2VecAudio Model with a language modeling head on top for Connectionist Temporal Classification (CTC). Data2VecAudio was proposed in data2vec: A General Framework for Self-supervised Learning in Speech, Vision and Language by Alexei Baevski, Wei-Ning Hsu, Qiantong Xu, Arun Babu, Jiatao Gu and Michael Auli.  For more information visit, https://huggingface.co/docs/transformers/model_doc/data2vec


```py
# pretrianed model 
BASE_MODEL = "./train/data2vec-thai-pretrained/1"
# load data
mixed_train = load_dataset("./cv11_dataloader.py", "th", split="train+validation")
mixed_test = load_dataset("./cv11_dataloader.py", "th", split="test")
# processor
processor = Wav2Vec2Processor.from_pretrained("./train/processor")
# import Waveaugment
import sys
sys.path.append("./train/WavAugment")
# clips path
abs_path_to_clips = "../data/commonvoice11/clips" 
```
### Evaluation
#

For our trained models can be downloaded below or run this script  to automatically download all models:
```
bash ./load_models.sh
```
- trained with the 1st dataset (original ratio of gender) 
<a href="https://drive.google.com/drive/folders/1YPmUk3ZsfMxqq2nFwUV3fWL3uKFxz13q?usp=sharing">load model</a>

- trained with the 2nd dataset (balance ratio between female & male)
<a href="https://drive.google.com/drive/folders/19ufxw8j2jOt3t8_a3Li5tIzMI2idicVk?usp=sharing">load model</a>

- trained with the 3rd dataset (balance ratio between female & male with speaking same sentence) 
<a href="https://drive.google.com/drive/folders/10DZLSO6ftUzZlvfme2FMbUIpH2ZZoYvS?usp=sharing">load model</a>

Model after upsampling training set:

Data upsampling by applying our gender classification model to identify genders for "not-filling" class.

- trained with the 2nd dataset including upsampling data (balance ratio between female & male) 
<a href="https://drive.google.com/drive/folders/1nsyl3VLo76DIRNg0Zrrrvy_o4QYlUtXJ?usp=sharing">load model</a>

- trained with the 3rd dataset including upsampling data (balance ratio between female & male with speaking same sentence)
<a href="https://drive.google.com/drive/folders/1lBu9JD-_cQOBjsN747ElV-kAsAhR6rD6?usp=sharing">load model</a>


```py
# processor
self.processor = Wav2Vec2Processor.from_pretrained("./train/processor")

# model 
model_path = <MODEL_PATH>
lm_path = "./train/newmm_4gram.bin" 

# you must first specify a dataset
dataset_name = "dataset_1"
cv11_test_paths = [
                  "../data/commonvoice11/annotation/dataset_1/test.csv" # Test set
                 ]

audio_paths = [
              "../data/commonvoice11/clips/clips_wav"
              ]

```
- Output of this  `data2vec_evaluate.py` is .csv file with WER and CER score per reccord, which you can easily group by gender to see the final results.





