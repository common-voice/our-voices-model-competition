# Preliminary note
Please check <https://github.com/hromi/our-voices-model-competition/releases/tag/v0.0.1> for all more massive files relevant to this submission.


# Abstract
One main "band C" output of our Mozilla "our voices 2022 competition" is a first publicly available, light-weight (e.g. DeepSpeech) speech-to-text acoustic & language model intentionally covering both Slovak (SK) as well as Czech (CS) poles of SlovakoCzech language continuum. Departing from the postulate that Slovak (SK) and Czech (CS) language are two variants of a common ancestor language, we create a common alphabet file for CS and SK, and transfer-learn an already available CS checkpoint file with SK and CS Common Voice data. Given that we use a common alphabet for both CS and SK, we can use a sort-of "disrupt & focus" procedure where we iteratively train the model with few epochs of CS (disrupt) following with few epochs of SK (focus). We obtain encouraging (WER: 15.8%; CER: 4.5%) results when testing on 500-utterance subset of CommonVoice's Slovak recordings data which weren't used during training. We obtain more modest results when we test the system on a real-life TEDxSK dataset (46% WER for female and 47,8% WER for male TEDx speakers). Additionally, the very same sk-focused acoustic model yields 32% WER for testing data contained in Czech language Common Voice dataset. One single epoch of subsequent focusing of the model to CS language yields a model with perform better for CS language (22% WER) while still preserving significant part of its ability to realize accurate inferences for SK as well. It is also observed that feeding a CS-input into SK-focused acoustic model and SK-scorer sometimes results in an interesting behaviour reminiscient of machine translation. The models hereby introduced can be immediately used for process of upvoting of not-yet-validated items of SK (resp. CS) Common Voice dataset and the method can be potentially used incases where multiple under-represented languages form a linguistic group or dialect continuum (c.f. also the [HighSorbian](https://github.com/hromi/our-voices-model-competition/tree/main/submit/Variant_Accent_Dialect/HighSorbian-band-A) subdirectory).


# Introduction
Question "Are czech (CS) and slovak (SK) two different languages or just two variants of one single language ?" is not an easy one to tackle. On one hand, one observes differences between CS and SK on phonetic, lexical and partially also morphosyntactic level. Phonetic differences, for example, express themselves in slight difference of alphabets of two languages: thus, CS alphabet contains letters "ř", "ě" and "ů" not contained in SK alphabet. Conversely, SK language - and SK alphabet - operates with phonemes (resp. letters) "ľ", "ĺ", "ŕ", "ô" and "ä" unbeknown to CS world.

Still, people who masters both CS and SK languages usually agree that there are more similarities than their are differences. Historically, both languages stem from the common root and the commong linguistic ancestor is still not so distant as, for example, in case of Dutch and German. Our Mozilla our-voices submission also departs from the premise that both languages can be understood as variants, or poles of a dialect continuum. Adoption of such a premise allows us to leverage a much bigger dataset of available recordings for CS language for the purpose of training of a SK speech-to-text system.

## Training the first public SK STT model

**In conrete terms, we consider CS and SK to be two distinct language variants of a common language**. This allows us to benefit from already existing resources - e.g. publicly available DeepSpeech checkpoint file for CS language - to fine-tune Slovak model with Common Voice data. This is of non-negligible advantage given that SK Common Voice dataset (18 hours of validated speech data; 19 hours in total) is significantly smaller than the CS one (59 hours of validated data; 70 hours in total).

# Method

## Common alphabet

An common CSK alphabet was created as a union of set of symbols included in CS and SK alphabets. CSK alphabet contains 43 symbols. In order to reduce the number of output neurons - and thus also the number of parameters and complexity of the acoustic model - the CSK alphabet does not contain the czech "ů" and slovak "ĺ" but these can be easily an unambigously identified. C.f. substitution regexes in the comments alphabet file's header to see how this can be done.

Having a common alphabet allows us to switch from CS to SK - or vice versa - with a simple fine-tuning procedure. Otherwise, more complex transfer learning procedure would be necessary.

## Datasets
We used two  Common Voice 11 Czech dataset and Common Voice 11 Slovak dataset for training and <!---own "toy" corpus to assess whether the SK model is good enough to be used in highly noise environment--> manually annotated part of the TEDxSK dataset for additional testing.

In case of CS corpus which is >3 times bigger than the SK corpus, we used train.csv (14612 items) and test.csv (7709) as generated by import\_cv2.py script included in the bin directory of the DeepSpeech project. 

<!---Additionally, cs/test-female.csv and csv/test-male.csv subdatasets thanks to metadata contained in CV's TSV files.--!>

In case of much smaller SK corpus, we decided to benefit from the fact that 16502 recordings have already been validated by Common Voice community. In order to have as much training data as possible, we used - out of 16502 rows of validated.csv file generated by the import\_cv2.py script -  first 16002 for training (train16002.csv) and last 500 for testing (test500.csv). Unfortunately, we later realized that this decision - which allowed us to use as much data as possible for training - this did not allow us to perform gender-specific evaluations given that all recordings from test500.csv seem to be recorded by one or few male speakers.

Thus, the amount of training recordings originating from CS dataset (14612) was more or less in balance with amount of SK training ones (16000). 

After some searching, we also found TEDxSK corpus. Being unsure about quality of its automatically created annotations, we used only the manually annotated part of it, extracted transcripts from sub-title (\*.stm) format and worked only with annotations which do not contain any stm/annotation-specific characters. This yielded datasets  TSDxSKfemale and TSDxSKmale of sufficient length (2060 recordings, resp. 5288 recordings). In the context of "our voices" competition, TEDxSK was not used for training at all.


<!---Based on gender information from Common Voice repository, train-female and train-male subdatasets were created for both languages. Gender-specific datasets were also created for those files included in the Common Voice - listed in others.tsv file - which are not yet considered to be neither validated nor invalidated.

Toy corpus contains recordings of one male and one female speaker of >20 strophes of a children alphabetisation verse book "Painted alphabet" by Slovak poet Jan Smrek. Toy corpus was created in real life conditions - e.g. a lot of noise, children running around, speaker making mistakes etc. - by means of a Raspberry PiZero with Respeaker 2-mic array embooked into a wooden shell of a "Digital Primer" artefact. As of 12.10 we did not yet time to fully validate all recordings of the corpus.
-->

## Training process

### Transfer learning

Training process is initiated by transfer learning from existing DeepSpeech model for Czech language - we call this model cs-origin - available here <https://github.com/comodoro/deepspeech-cs/> . Release from 21st July 2021 contains checkpoint file among its assets, so that's where we start.

We drop just the last layer ( --drop\_source\_layers 1) during the transfer learning process.  

### Disrupt \& Focus

We used a method which we naively call "disrupt & focus". During the disrupt epoch (or a certain number of epochs), model is trained with data originating from language X. Subsequently, during the focus epoch - or a certain number of epochs - model is trained solely with data originating from language Y. Disrupt & focus couples sequence can be repeated multiple times, always ending with at least one focus epoch which adapts the model primarily to target language Y. The intuition behind the usage of "disrupt" epochs is to use non-target yet similar-to-target language X to get model out of locally optimal state, thus reducing the danger of overfitting.

Note that given that both X and Y share the common alphabet, switch between language X and Y does not oblige one to drop any layer nor change of amount of neurons in the output layer. 

#### Models

Our main output - the model sk-focused - has been obtained by:

* transfer-learning (10 epochs) from cs-origin to new alphabet with samples from sk/train16002.csv
* disrupting the model with 1 epoch of training with cs/train.csv
* pre-focusing the model with 10 epochs of training with sk/train160002.csv
* re-disrupting the model with 1 epoch of training with cs/train.csv
* focusing the model with 10 epochs of training with sk/train160002.csv

Our secondary output - the model cs-generic - has been obtained by focusing the sk-generic to samples from cs/train.csv for one single epoch.

## Scorers

We created a first publicly available language model of slovak language (sk-dictwiki.scorer) by combining the wikipedia data with enriched dictionary of slovak language. Publicly available wikipedia dump was transformed in pure text corpus by a wonderful WikiExtractor tool ( <https://github.com/attardi/wikiextractor> ). Morphologically enriched dictionary was obtained as a dump from aspell package

`aspell --lang sk dump master | aspell --lang sk expand | tr ' ' '\n' > sk-dictionary.txt`

Well-established tools from DeepSpeech \& KenLM suite are used to create the scorer. To simplify the process for future generations, we package all necessary command in script utils/new\_scorer\_from\_file.sh. We used most frequent milion words to create the scorer, these cover 96.3% of tokens 

## Evaluation

Our main evaluation metric were WER / CER error rates, as returned by the DeepSpeech script for different model / test-data combinations. 

We also looked at number of "complete match" predictions with ideal (i.e. zero) WER. 

We denote quantity of such "complete match" prediction with as M and proportion of fully matched items present in dataset of size N as N/M.

# Results

Model         | Tested on         | WER     |CER     | Loss    |Scorer     |M 
--------------|-------------------|---------|--------|---------|-----------|----
sk-focused    |sk/train16002.csv\*| 0.096608|0.021378|3.950855 |sk-dictwiki|2373
sk-focused    |cs/train.csv\*\*   | 0.132358|0.045967|31.222963|cs-dictwiki|7870
sk-focused    | sk/test500.csv    | 0.150977|0.043060|14.073430|sk-all     |324
sk-focused    | sk/other.csv      | 0.275912|0.098194|16.803932|sk-all     |96
sk-focused    | cs/test.csv       | 0.327879|0.138786|43.103512|cs-all     |2010
sk-focused    | cs/test.csv\*\*\* | 0.652641|0.236816|43.103512|sk-all     |2010
sk-focused    | TEDxSK/female.csv | 0.460184|0.241200|54.737408|sk-all     |373
sk-focused    | TEDxSK/male.csv   | 0.478214|0.260343|59.606163|sk-all     |1039

\* Note that train16002.csv was used to train the sk-focused model, therefore the encouraging 2.1% CER in the first test can potentially be caused to overfitting and not due to induction of useful generalizations.

\*\* Note that information contained in cs/train.csv was used in the disrupt phase which occured sometimes in previous (disrupt) stages of the model training.

\*\*\* Interesting phenomena observed, c.f. "Noteworthy phenomena" subsection of "Discussion" section

Model     | Tested on     | WER    |CER     | Loss    | scorer
----------|---------------|--------|--------|---------|----------
cs-focused| cs/test.csv   |0.225018|0.100922|23.676527|cs-dictwiki
cs-focused|sk/test500.csv |0.349023|0.125830|28.343493|cs-dictwiki
cs-focused|TEDxSK/male.csv|0.670467|0.378538|75.238403|cs-dictwiki


Not yet validated    | model      | scorer | M  | N/M ratio
---------------------|------------|--------|----|----------
sk/other.csv (N=182) | sk-generic | sk-all | 96 | 51.6 %     
cs/other.csv (N=8532)| cs-generic | cs-all | 732| 11.7 % 


# Discussion

## Utility

In the context of Mozilla's 2022 edition of Our Voices Competition, we have created first publicly available Deepspeech/[Coqui](https://coqui.ai) STT system for Slovak language. System is composed of a 181 Megabyte acoustic model derived from publicly available checkpoints of Czech Deepspeech model and a 180 Megabyte language model able to execute fast enough inferences even on a Raspberry Pi. The system performs encouringly well (~15% WER) when tested against CommonVoice sentences not used during the training. Tests agains real-life conditions (e.g. TEDxSK) do not point to presence of any pro-male bias (i.e. 46% WER for emale, 47.8% WER for male) but further work - e.g. training with non-CommonVoice datasets - should be and will be done.

Last table of the "Results" section indicates immediate utility of our system for CV community: transcripts of more than half (e.g. 51.6 \%) of samples which are still not validated in the Slovak corpus match predictions given by our Slovak STT system. One can thus potentially upvote such recordings and/or consider them as validated by a validator of artificial nature, thus reducing the amount of manpower for the validation process.

At last but not least, our "common alphabet for a dialect continuum approach" can be useful also for highly underrepresented languages - c.f. our Band A - "[HighSorbian](https://github.com/hromi/our-voices-model-competition/tree/main/submit/Variant_Accent_Dialect/HighSorbian-band-A)" - subdirectory of our submission.

## Environment

All training and testing took place on an Nvidia Xavier Jetson Dev Kit with Jetpack 4.6 running Deepspeech 0.9.3 with GPU (CUDA) support. Given that original CS model was trained without automatic precision and without cuDNN support, our derived models were also trained without this acceleration mechanisms. Last time I checked it in my office, it looked like this:

![Jetson in action](https://github.com/hromi/our-voices-model-competition/blob/main/submit/Variant_Accent_Dialect/SlovakoCzech-band-C/JetsonCommonVoice.jpeg?raw=true)

so it is almost certain that since 14 days uptime it dedicated some of its cycles to our voices competition, it consumed less than 10 kW of energy.

# Noteworthy phenomena

After exposing czech recordings to sk-focused acoustic model combined with sk-dictwiki scorer, one observes cases when our systems behaves like a trivial CS-SK translation engine. For example:

`
WER: 0.666667, CER: 0.097561, loss: 33.360397
 - wav: file://common_voice_cs_22381929.wav
 - src: "jezdilo se proti směru hodinových ručiček"
 - res: "jazdilo sa proti smeru hodinových ručičiek"
`

whereby the predicted sequence "jazdilo sa proti smeru hodinových ručičiek" is a phonetically and syntactically correct slovak translation of the original czech utterance. 

Limits of WER / CER metrics in such cases are obvious.

# Checkpoint

In <https://github.com/hromi/our-voices-model-competition/releases/tag/v0.0.1> we also provide checkpoint file for sk-focused so that other can continue there, where we halt.

# References
* [deepspeech-cs](https://github.com/comodoro/deepspeech-cs)
* [TEDxSK](https://nlp.kemt.fei.tuke.sk/speech/tedx) J. Staš, D. Hládek, P. Viszlay, T. Koctúr, “TEDxSK and JumpSK: A new Slovak speech recognition dedicated corpus,” Journal of Linguistics, Vol. 68, No. 2, 2017, pp. 346-354.
* [Common Voice](https://commonvoice.mozilla.org/)
* [WikiExtractor](https://github.com/attardi/wikiextractor) / [Wikipedia dumps](https://dumps.wikimedia.org/backup-index.html)
* [Deepspeech command-line flags for training scripts ;)](https://deepspeech.readthedocs.io/en/latest/Flags.html)


# Comment to our-voice competition jury

In certain sense, our work is also relevant to "Method" and "Open" categories but being unsure whether we can apply in multiple categories in the same time, we put it into "Language Variant" section.

