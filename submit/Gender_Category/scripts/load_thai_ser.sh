echo "Install essential libraries"
pip install -r ./requirements.txt

cd ../data

echo "Download Thai-SER dataset"
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

echo "Unziping Thai-SER"
cd ./raw
unzip '*.zip' -d ../thai_ser/raw


echo "Preprocessing audio files"
cd ..
python ../scripts/preprocess.py --ds_root="./thai_ser/raw" --dst_root="./thai_ser/clips/preprocess/wav_file"

echo "\n DONE \n"
echo "All datasets used in this project are processed and stored in /submit/Gender_Category/data"
echo "Data for gender classification: /submit/Gender_Category/data/thai_ser"