# Common voice dataset

Place a common voice archive in this folder.

Run `unpack.py` for both train an test datasets

    $ ./unpack.py train.tsv train
    $ ./unpack.py test.tsv test

If the gender of a speaker is unidentified, you'll be asked to determine the gender by hear after playing a voice sample.
Press `m` for male, `f` for female, `u` if unknown, `x` to skip this process or any other key to listen to another sample.

## Script compare_tsv

`compare_tsv.py` is a tool to get information about a `tsv` file, or to compare two `tsv` files.

Usage:
    $ python3 compare_tsv.py dev.tsv
    $ python3 compare_tsv.py train.tsv test.tsv

## Script extract_vocabulary

`extract_vocabulary.py` extracts the vocabulary from a `tsv` file and outputs a list of words along with the number of occurences in file `mcv_vocab.txt`. This file is sorted by number of occurences, reversed (most common words firts).

Usage:
    $ python3 extract_vocabulary.py dev.tsv
