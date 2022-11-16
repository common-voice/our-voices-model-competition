#use to transform canonic czech to common western slavic alphabet, use with deepspeech import CV script
#python3 ./bin/import_cv2.py --filter_alphabet ./alphabet.txt --validate_label_cs_labels.py

from num2words import num2words
import re
def validate_label(label):
    label=label.lower()
    try:
        label=num2words(label, lang='cz')
    except:
        1
    label=label.replace('ů','ú')
    label=re.sub('[^ abcdefghijklmnopqrstuvwxyzáéíóúýôäčďľěňŕšťžř]','',label)
    return label # lower case valid labels
