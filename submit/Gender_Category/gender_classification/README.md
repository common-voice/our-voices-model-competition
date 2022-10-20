# Gender classifier

### Overview
This model is simply a stack of 5 TDNN modules on top with 2 layers of Fully-connected. This model trained on 2 dataset; commonvoice11-th, Thai-ser.
For more information please visit, https://github.com/speechbrain/speechbrain/tree/main/templates/speaker_id

### Setup
First, please execute the following command before start training or inference.
```
bash ./setup.sh
```
This script will automatically download the essential files and also install dependencies from `../requirements.txt`

### Sample Usage
- Model Initiation

```py
import torchaudio
from speechbrain.pretrained import EncoderClassifier

model = EncoderClassifier.from_hparams(
    source="./pretrained_model", 
    hparams_file="./hparams_inference.yaml", 
    savedir="./save"
    )
```
See Also
EncoderClassifier: https://github.com/speechbrain/speechbrain/blob/develop/speechbrain/pretrained/interfaces.py#L823

- Inference

To inference the pretrained model from our team, execute the following commands
```py
audio_path = "path/to/audio.wav" # Path to audio file, Support only .wav format with 16kHz
signal, fs = torchaudio.load(audio_path) 
output_probs, score, index, class_pred = model.classify_batch(signal)
```

Sample Output
```
>>> class_pred[0]
    'Male'
```

To inference whole dataset of commonvoice11 visit `./model_inference.ipynb`. This script will iterate through all data in commonvoice11's directory and assign gender to each `client_id`


### Train
This model trained on 2 datasets
 - Commonvoice11-thai
 - Thai-SER

Please download these datasets before execute model training by running 
```console
cd ../data
bash ./load_dataset.sh
```

We utilized Speechbraind to train the model.
visit https://github.com/speechbrain/speechbrain/tree/main/templates/speaker_id

Annotation files already provided in `./train/manifest`. Annotation generator also provided in `./train/manifest/annotation_generator.ipynb`
To reproduce our work, use this command

```py
cd ./train
python train.py train.yaml
```
