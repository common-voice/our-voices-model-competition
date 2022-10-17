## STT finetune 

### Setup

```
pip install -r requirements.txt
```

Then, download followings or download sh file 

- <a href="https://drive.google.com/drive/folders/1zM_yEi0eEiAItiVSIlQeSgIGderRemHu?usp=sharing">Pretrained model</a>
- <a href="https://drive.google.com/drive/folders/1bsj7DV6Y9hYf4C-Tx0P6tmvPr2hJtwsp?usp=sharing">Processor</a>
- <a href="https://drive.google.com/file/d/1TX-Fp9CWz7U2AicAjhy3gmDoM7XHqSty/view?usp=sharing">Language Model</a>
- <a href="https://drive.google.com/drive/folders/1LAkmsgQ1KrxuFO54UOTnrA7NWcOGAshX?usp=sharing">WavAugment</a>

```
bash ./setup.sh
```
This will automatically download the essential files for model training.




### Model training
Our base model is Data2VecAudio Model with a language modeling head on top for Connectionist Temporal Classification (CTC). Data2VecAudio was proposed in data2vec: A General Framework for Self-supervised Learning in Speech, Vision and Language by Alexei Baevski, Wei-Ning Hsu, Qiantong Xu, Arun Babu, Jiatao Gu and Michael Auli.  For more information visit, https://huggingface.co/docs/transformers/model_doc/data2vec


```py
# pretrianed model 
BASE_MODEL = "./data2vec-thai-pretrained"
# load data
mixed_train = load_dataset("./cv11.py", "th", split="train+validation")
mixed_test = load_dataset("./cv11.py", "th", split="test")
# processor
processor = Wav2Vec2Processor.from_pretrained("./processor")
# import Waveaugment
import sys
sys.path.append("./WavAugment")
# clips path
abs_path_to_clips = "./Methods_and_Measures/commonvoice11/data/clips_wav" 
```

For our trained models can be downloaded below:

- trained with the 1st dataset (original ratio of gender) 
<a href="https://drive.google.com/drive/folders/1YPmUk3ZsfMxqq2nFwUV3fWL3uKFxz13q?usp=sharing">load model</a>

- trained with the 2nd dataset (balance ratio between female & male)
<a href="https://drive.google.com/drive/folders/19ufxw8j2jOt3t8_a3Li5tIzMI2idicVk?usp=sharing">load model</a>

- trained with the 3rd dataset (balance ratio between female & male with speaking same sentence) 
<a href="https://drive.google.com/drive/folders/10DZLSO6ftUzZlvfme2FMbUIpH2ZZoYvS?usp=sharing">load model</a>

Model after upsampling training set:

- trained with added 2nd dataset (balance ratio between female & male) 
<a href="https://drive.google.com/drive/folders/1nsyl3VLo76DIRNg0Zrrrvy_o4QYlUtXJ?usp=sharing">load model</a>

- trained with added 3rd dataset (balance ratio between female & male with speaking same sentence)
<a href="https://drive.google.com/drive/folders/1lBu9JD-_cQOBjsN747ElV-kAsAhR6rD6?usp=sharing">load model</a>

### Evaluation
#
```py
# processor
self.processor = Wav2Vec2Processor.from_pretrained("./processor")

# model 
model_path = <MODEL_PATH>
lm_path = "./newmm_4gram.bin" 

# test set 
cv11_test_paths = [
                  "./test.csv"
                 ]
# clips path
audio_paths = [
              "./Methods_and_Measures/commonvoice11/data/clips_wav"
              ]

```
- Output of this  `data2vec_evaluate.py` is .csv file with WER and CER score per reccord, which you can easily group by gender to see the final results.





