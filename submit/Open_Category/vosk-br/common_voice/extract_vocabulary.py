#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
sys.path.append("..")
from libMySTT import get_cleaned_sentence


blacklisted_speakers_file = "blacklisted_speakers.txt"
blacklisted_sentences_file = "blacklisted_sentences.txt"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "tsv_file")
    
    blacklisted_speakers = []
    if os.path.exists(blacklisted_speakers_file):
        with open(blacklisted_speakers_file, 'r') as f:
            blacklisted_speakers = [l.split()[0] for l in f.readlines()]
    else:
        print("Blacklist speaker file not found")
    
    blacklisted_sentences = []
    if os.path.exists(blacklisted_sentences_file):
        with open(blacklisted_sentences_file, 'r') as f:
            blacklisted_sentences = [l.strip() for l in f.readlines() if not l.startswith('#')]
    else:
        print("Blacklisted sentences file not found")
    
    
    vocabulary = dict()
    
    with open(sys.argv[1], 'r') as f:
        f.readline() # skip header
        for l in f.readlines():
            l = l.strip().split('\t')
            speaker_id = l[0][:16]    # Shorten speaker-id
            if speaker_id in blacklisted_speakers:
                continue
            if l[2] in blacklisted_sentences:
                continue
            
            corrected, _ = get_cleaned_sentence(l[2])
            for word in corrected.split():
                if word in vocabulary:
                    vocabulary[word] += 1
                else:
                    vocabulary[word] = 1
    
    with open("mcv_vocab.txt", 'w') as f:
       for w, n in sorted(vocabulary.items(), key=lambda x: x[1], reverse=True):
           f.write(f"{w}\t{n}\n")
    
