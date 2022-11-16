#first purify Your STM subtitles with something like
#You need to have Your wave_files in ./dataset and You need to have ./cut where segmented utterances will be stored
#cat *.stm |perl -ne '/(\d\d\d_tedxsk_\w+) (\d+.\d+) (\d+.\d+) <.*?> (.*)$/;$f=$1;$start=$2;$stop=$3;$t=$4;$t=~s/\[.*?\]/ /g;print "$f;$start;$stop;$t\n" if ($t!~/[%(*@^]/ and $t);' |uniq |less >TEDxSKpure.csv 
#then run this script with
#python3 tedx2deepspeech.py <TEDxSKpure.csv >TEDxDeepspeech.csv 
#voila, You can use TEDxDeepspeech.csv aas test_files resp. dev_files train_files of Your Deepspeech training process

import os,re,sys
from pydub import AudioSegment

path=os.getcwd()

id=0
print("wav_filename,wav_filesize,transcript")

for line in sys.stdin:
    items=line.split(';')
    (f,s,gender)=items[0].split('_')
    talk = AudioSegment.from_wav(path+'/dataset/'+f+'_'+s+'.wav')
    utterance=talk[int(float(items[1])*1000):int(float(items[2])*1000)]
    #print(str(int(float(items[2])*1000)-int(float(items[1])*1000)))
    #print(utterance.duration_seconds)
    cutpath=path+'/cut/'+f+'_'+s+'_'+gender+'_'+str(id)+'.wav'
    utterance.export(cutpath,format="wav")
    #adapt to Your alphabet
    transcript=re.sub('[^ abcdefghijklmnopqrstuvwxyzáéíóúýôäčďľěňŕšťžř]','',items[3])
    print(cutpath,",",os.path.getsize(cutpath),",",transcript)
    id=id+1


