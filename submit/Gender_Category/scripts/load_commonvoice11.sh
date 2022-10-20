echo "Install essential libraries"
pip install -r ./requirements.txt

cd ../data

echo "Download the Common Voice 11 dataset for Thai"
# Commonvoice11
wget https://mozilla-common-voice-datasets.s3.dualstack.us-west-2.amazonaws.com/cv-corpus-11.0-2022-09-21/cv-corpus-11.0-2022-09-21-th.tar.gz -P ./raw

# Download additional files
gdown 1g4eNwB23ZJrAyZhJlw5vjkZ7mN0m-sut
mkdir -p ./commonvoice11/annotation/dataset_2_add_gender
mv ./added_gender_balanced_train_data20201011.xlsx ./commonvoice11/annotation/dataset_2_add_gender/train.xlsx

gdown 1AtsmxY2pCAEiajxRuJ1U5w4FPkVLbscd
mkdir -p ./commonvoice11/annotation/dataset_3_add_gender
mv ./added_gender_balanced_same_sentence_train_data20201011.xlsx ./commonvoice11/annotation/dataset_3_add_gender/train.xlsx

gdown 12KJ8VKK9Ny190Yx95-uU2XHe7l3Q9g45
mkdir -p ./commonvoice11/annotation/dataset_3
mv ./test_trimmed_with_cer.csv ./commonvoice11/annotation/dataset_3/test_trimmed_with_cer.csv

echo "Unziping the Common Voice 11 dataset for Thai"
mkdir -p ./commonvoice11/raw
tar -xf ./raw/cv-corpus-11.0-2022-09-21-th.tar.gz -C ./commonvoice11/raw

# Copy extracted validated.tsv to ./commonvoice11/annotation
cp ./commonvoice11/raw/cv-corpus-6.1-2020-12-11/th/validated.tsv ./commonvoice11/annotation

echo "Preprocessing the Common Voice 11 dataset for Thai"
# Preprocess file
python ../scripts/preprocess.py --ds_root="./commonvoice11/raw/cv-corpus-11.0-2022-09-21/th/clips" --dst_root="./commonvoice11/clips/clips_wav"

echo "\n DONE \n"
echo "All datasets used in this project are processed and stored in /submit/Gender_Category/data"
echo "Data for STT: /submit/Gender_Category/data/commonvoice11"