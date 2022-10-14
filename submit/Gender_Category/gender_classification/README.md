# Gender classifier

### Overview
This model is simply a stack of 5 TDNN modules on top with 2 layers of Fully-connected. This model trained on 2 dataset; commonvoice11-th, Thai-ser.
For more information please visit, https://github.com/speechbrain/speechbrain/tree/main/templates/speaker_id

### Setup

```
bash ./setup.sh
```
This script will automatically download the essential files and also install required libraries.

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
```py
signal, fs = torchaudio.load(audio_path) 
output_probs, score, index, class_pred = classifier.classify_batch(signal)
```

Sample Output
```
>>> class_pred[0]
    'Male'
```