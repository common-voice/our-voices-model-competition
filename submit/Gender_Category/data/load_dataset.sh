# Download datasets; Thai-SER for gender classification training
# And Commonvoice11
echo "Install essential libraries"
pip install -r ./requirements.txt

# echo "Download Thai-SER dataset"
# Thai-SER
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/studio1-10.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/studio11-20.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/studio21-30.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/studio31-40.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/studio41-50.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/studio51-60.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/studio61-70.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/studio71-80.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/zoom1-10.zip -P ./raw
wget https://github.com/vistec-AI/dataset-releases/releases/download/v1/zoom11-20.zip -P ./raw

echo "Download Commonvoice11"
# Commonvoice11
wget https://mozilla-common-voice-datasets.s3.dualstack.us-west-2.amazonaws.com/cv-corpus-11.0-2022-09-21/cv-corpus-11.0-2022-09-21-th.tar.gz -P ./raw

# Additional download
mkdir annotation
cd ./annotation
gdown 12KJ8VKK9Ny190Yx95-uU2XHe7l3Q9g45

gdown 1g4eNwB23ZJrAyZhJlw5vjkZ7mN0m-sut
mv ./added_gender_balanced_train_data20201011.csv ./commonvoice11/annotation/dataset_2_add_gender/train.csv

gdown 1AtsmxY2pCAEiajxRuJ1U5w4FPkVLbscd
mv ./added_gender_balanced_same_sentence_train_data20201011.csv ./commonvoice11/annotation/dataset_3_add_gender/train.csv

# Unzip all files
cd ../raw
echo "Unziping Commonvoice11"
mkdir -p ../commonvoice11/raw
tar -xf ./cv-corpus-11.0-2022-09-21-th.tar.gz -C ../commonvoice11/raw
echo "Unziping Thai-SER"
unzip ./*.zip -d ../thai_ser/raw

echo "Preprocessing Commonvoice11 & Thai-SER"
# Preprocess file
cd ..
python preprocess.py --ds_root="./commonvoice11/raw/cv-corpus-11.0-2022-09-21/th/clips" --dst_root="./commonvoice11/clips/clips_wav"
python preprocess.py --ds_root="./thai_ser/raw" --dst_root="./thai_ser/clips/preprocess/wav_file"

echo "\n DONE \n"
echo "All datasets used in this repository are processed and stored in ./submit/Gender_Category/data"
echo "For Commonvoice11: ./commonvoice11/clips/clips_wav"
echo "For Thai-SER: ./thai_ser/clips/preprocess/wav_file"
