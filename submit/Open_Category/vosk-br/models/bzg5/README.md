# Breton Vosk Model v5

24-06-2022

lexicon: **36 581 words** with phonemes \
corpus: **1 693 532 words**

Test "Bali Breizh er Poc'hêr : Karaez 1" : **48.5% WER** \
Test Baleadenn1.wav :
> "Gant ar sorserezh oa ur <del>c'harr</del> \
> Hag un <del>tammig</del> uhel ha bras"


## Train Datasets

13 612 utterances

Total audio length:	**15h 49'46''** \
Male speakers: **10h 36'14''**  (67%) \
Female speakers: **5h 13'32''**    (33%)

  * Dizale
    * Kabellig_Ruz
    * Oceanopolis
    * Nelson Mandela
    * Birmania
    * Wangari Mathai
    * Lampedusa Beach
    * Film "Ar Vreudeur Bloom"
  * Brezhoweb - Pennad Kaoz
    * Izold Guegan
    * Katell Chantreau
  * Kelaouen #Brezhoneg, Skol An Emzav
    * n° 11-12, 14-44
  * Common Voice 7.0 train set
  * RKB
    * Atersadenn-war-eeun-Jeannot-Flaguel
    * Isabelle Caignard - Skampiola
  * Other
    * Anna Loeiza - Pemzek teiz (FR3)



# Test Dataset

2 053 utterances

Total audio length:	**1 h 55'49''** \
Male speakers:	**1 h 17'47''**	(67%) \
Female speakers:	**0 h 38'2''**	(33%)

  * Common Voice 7.0 test set



# Remarks

This model has been improved over the last one by joining short utterances together (< 2 seconds) to form utterances of acceptable length. \
74 777 sentences from breton wikipedia added to the text corpus. \
The vocabulary is now 3 times bigger than previous model (bzg3). \
"Isabelle Caignard - Skampiola" radio interview (Radio Kreiz Breizh) added to training data. \
"Anna Loeiza - Pemzek teiz" tv interview (France3 région Bretagne) added to training data. \
"Bali Breizh" score is slightly better than previous model (bzg3 54.4% WER)
