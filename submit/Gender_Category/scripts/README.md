# Download & Preprocess datasets.
This directory is for dataset downloading and preprocessing. To download each dataset, please execute the following commands.
There're 2 scripts for Commonvoice11-th and Thai-SER. For each contain download and preprocess command.
For more information about preprocessing, visit `preprocess.py`.

## Download & Preprocess Commonvoice11-th
```
bash ./load_commonvoice11.sh
```

## Download & Preprocess Thai-SER for gender classifier
```
bash ./load_thai_ser.sh
```

After preprocess all audio files, processed files will be stored in `../data/{dataset_name}/clips`
For Commonvoice11 `../data/commonvoice11/clips`. For Thai-SER `../data/thai_ser/clips`