#DeepSpeech for HighSorbian (deepspeech-hsb)

Very briefly here: we took a deepspeech-cs checkpoint, originally trained on Czech audio recordings, transfer-learned it to our WesternSlavic alphabet.txt, trained some more epochs on Slovak-Czech-Slovak data to finally focus it on HSB in the following process:

* first 5 epochs of training on train (N=808) until validation with validation set (N=173) stops decreasing
* than 1 epoch of training on validation set
* than 1 epoch of training on both train + validation (N=971) set
* 1 epoch of training on train + validation + fragments \* set

Once this process is over, we get WER: 0.545715, CER: 0.218711, loss: 66.486069  on 450 recordings in testing CommonVoice sub-dataeset. Without fragment enrichment, results are WER: 0.568155, CER: 0.233091, loss: 69.035698.

#Model, scorer, alphabet
What You need to get You started is here: 

#Read before use
If You want to use this in Your system, make sure that You execute following non-ambigous substitutions, to make HSB consistent with WesternSlavic alphabet:
`
replace('ł','v')
replace('ć','ť')
replace('ń','ň')
replace('ź','zz')
`
for inputs into the system (c.f. hc_labels.py code snippet for import_cv2.py CommonVoice-to-DeepSpeech importer)
`
python3 ./bin/import_cv2.py --filter_alphabet ./alphabet.txt --validate_label_locale hsb_labels.py /data/CommonVoice/hsb
`

Conversely, before displaying the outputs of Your STT system , You will need to apply inverse transformations:
`
replace('v','ł')
replace('ť','ć')
replace('ň','ń')
replace('zz','ź')
`

to show the Sorbian person what he/she wants to see. (For slovaks and czechs, the whole thing is more readable with westernslavic alphabet).


#Curious ?
Please read this <https://github.com/hromi/our-voices-model-competition/tree/main/submit/Variant_Accent_Dialect/SlovakoCzech#readme> to know more about why, what & how.


\* we'll go into more detail concerning the fragment method in a related academic paper.


