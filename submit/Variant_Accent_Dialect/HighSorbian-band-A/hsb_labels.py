#from num2words import num2words
import re
def validate_label(label):
    label=label.lower()
    #try:
    #    label=num2words(label, lang='cz')
    #except:
    #    1
    label=label.replace('ł','v')
    label=label.replace('ć','ť')
    label=label.replace('ń','ň')
    label=label.replace('ź','zz')
    label=re.sub('[^ abcdefghijklmnopqrstuvwxyzáéíóúýôäčďľěňŕšťžř]','',label)
    return label # lower case valid labels
