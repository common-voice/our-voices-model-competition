#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Build a text corpus from wikipedia br dumps
 Outputs text files:
    * "corpus/wiki_corpus.txt", the main corpus of sentences
    * "wikipedia_corpus/wiki_acronyms.txt", a list of possible acronyms
    * "wikipedia_corpus/wiki_capitalized.txt", a list of capitalized words
    * "wikipedia_corpus/wiki_sant.txt", a list of saints, convenient to retrieve first names
    * "wikipedia_corpus/wiki_vocab.txt", the vocabulary of the corpus
 
 Author:  Gweltaz Duval-Guennoc
  
"""


import os
import json
import re
from colorama import Fore
from libMySTT import filter_out, punctuation, valid_chars, hs_dict, capitalized, is_acronym, acronyms, get_cleaned_sentence, get_correction


LIMIT_VOCAB = True
VOCAB_SIZE = 10000



dumps_dir = os.path.join("wikipedia_corpus", "dumps")


PARENTHESIS_PATTERN = re.compile(r"\([^\(]+\)")

def extract_parenthesis(sentence):
    # Extract text between parenthesis
    in_parenthesis = []
    match = PARENTHESIS_PATTERN.search(sentence)
    while match:
        start, end = match.span()
        sentence = sentence[:start] + sentence[end:]
        in_parenthesis.append(match.group())
        match = PARENTHESIS_PATTERN.search(sentence)
        
    return [sentence] + in_parenthesis



def _split_line(s, splitter = '. '):
    length = len(splitter)
    if splitter in s:
        i = s.index(splitter)
        if len(s) > i + length and \
           (s[i+length].isupper() or not s[i+length].isalnum()) and \
           i > length and \
           s[i-length] != ' ':          
            # Ignore last occurence
            # Next letter must be upper case
            # Ignore if at begining of sentence
            # Previous word must not be a single letter (filter out acronyms)
            return [s[:i]] + _split_line(s[i+2:], splitter)
    return [s]



def split_line(sentence):
    sub = extract_parenthesis(sentence)
    splitters = ['. ', ': ', '! ', '? ', ';']
    
    for splitter in splitters:
        new_sub = []
        for s in sub:
            new_sub.extend(_split_line(s, splitter))
        sub = new_sub
    
    # filter out sub-sentences shorter than 2 tokens
    return [s for s in sub if len(s.split()) > 2]



def test_split_lines():
    sentences = [
        "Un tan-gwall a voe d'ar 1añ a viz Gouhere 2011 el leti. Ne voe den ebet gloazet pe lazhet. Un nebeud estajoù nemetken a oa bet tizhet.",
        "E 1938 e voe he gwaz harzet ha lazhet en U. R. S. S., ar pezh na viras ket ouzh Ana Pauker a chom feal d'ar gomunouriezh, d'an U. R. S. S. ha da Jozef Stalin.",
        "Ur maen-koun zo war lein, da bevar barzh eus ar vro : T. Hughes Jones, B.T. Hopkins, J. M. Edwards hag Edward Prosser Rhys.",
        """C'hoariet en deus evit Stade Rennais Football Club etre 1973 ha 1977 hag e 1978-1979. Unan eus ar c'hoarierien wellañ bet gwelet e klub Roazhon e oa. Pelé en deus lavaret diwar e benn : « "Kavet 'm eus an hini a dapo ma flas. Laurent Pokou e anv." ».""",
        """Hervez Levr ar C'heneliezh ec'h eo Yafet eil mab Noah. Hervez ar Bibl e tiskouezas doujañs e-kenver e dad mezv-dall. Benniget e voe gantañ evel Shem : "Frankiz ra roio Doue da Yafet ! Ha ra chomo e tinelloù Shem !" """,
        "Tout an dud en em soñj. Piv int ar skrivagnerien-se ? Eus pelec'h emaint o tont... ?",
        ]
    lengths = [3, 1, 2, 5, 5, 3]
    for i, s in enumerate(sentences):
        splits = split_line(s)
        print(s)
        print(len(splits))
        if len(splits) == lengths[i]:
            print(Fore.GREEN + "OK" + Fore.RESET)
        else :
            print(splits)
            print(Fore.RED + "FAIL" + Fore.RESET)
        print()




if __name__ == "__main__":
    articles = []

    for filename in os.listdir(dumps_dir):
        filename = os.path.join(dumps_dir, filename)
        with open(filename, 'r') as f:
            for line in f.readlines():
                articles.append(json.loads(line))
    
    keepers = set()
    acronym_words = set()
    capitalized_words = set()
    santou = set()
    num_outed = 0
    
    vocabulary = dict()

    for a in articles:
        for line in a["text"].split('\n'):
            for sentence in split_line(line):
                sentence = filter_out(sentence, punctuation + '*')
                words = sentence.split()
                
                # Filter out short sentences
                if len(words) <= 3:
                    continue
                
                first_word = True
                sant = False
                for w in words:
                    if sant:
                        if w.lower() not in capitalized:
                            santou.add(w)
                        sant = False
                    elif w == "Sant":
                        sant = True
                    
                    if is_acronym(w) and w not in acronyms:
                        acronym_words.add(w)
                    elif not first_word and w.istitle() and w.isalpha() and w.lower() not in capitalized:
                        capitalized_words.add(w)
                    first_word = False
                
                correction, num_errors = get_correction(sentence)
                if num_errors == 0:
                    cleaned_sentence, _ = get_cleaned_sentence(sentence)
                    keepers.add(cleaned_sentence)
                    for w in cleaned_sentence.split():
                        if w in vocabulary:
                            vocabulary[w] += 1
                        else:
                            vocabulary[w] = 1
                elif num_errors == 1:
                    #if num_outed % 200 == 0:
                    #    print(correction)
                    num_outed += 1

    #print(f"{num_outed} discarded sentences with 1 error")
    
    
    if LIMIT_VOCAB:
        voc_list = sorted(vocabulary.items(), key=lambda x: x[1], reverse=True)
        voc_list = voc_list[:VOCAB_SIZE]
        vocabulary.clear()
        vocabulary.update(voc_list)
    
    kept = 0
    save_dir = "corpus"
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    
    with open(os.path.join(save_dir, "wiki_corpus.txt"), 'w') as f:
        for sentence in keepers:
            # Keep sentences with common words only
            for w in sentence.split():
                if LIMIT_VOCAB and not w in vocabulary:
                    break
            else:   # Executed only if previous for loop exited normally
                if sentence.endswith(" ar") or sentence.endswith(" an"):
                    pass
                elif "ar kantved" in sentence or "an kantved" in sentence:
                    pass
                elif "er kantved" in sentence or "en kantved" in sentence:
                    pass
                else:
                    f.write(sentence + '\n')
                    kept += 1
    
    print(f"{kept} sentences kept")
    
    with open(os.path.join("wikipedia_corpus", "wiki_acronyms.txt"), 'w') as f:
        for a in sorted(acronym_words):
            f.write(a + '\n')
    with open(os.path.join("wikipedia_corpus", "wiki_capitalized.txt"), 'w') as f:
        for w in sorted(capitalized_words):
            f.write(w + '\n')
    with open(os.path.join("wikipedia_corpus", "wiki_sant.txt"), 'w') as f:
        for w in sorted(santou):
            f.write(w + '\n')
    with open(os.path.join("wikipedia_corpus", "wiki_vocab.txt"), 'w') as f:
        for w, n in sorted(vocabulary.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{w}\t{n}\n")
