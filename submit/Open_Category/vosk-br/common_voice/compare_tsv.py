#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author:        Gweltaz Duval-Guennoc
 
    Analyse (or compare) tsv files
 
"""


import sys
import os
import tarfile
from math import floor, ceil
from pydub import AudioSegment

sys.path.append("..")
from libMySTT import get_audiofile_length, get_cleaned_sentence



filtered_out = True

spk2gender_file = "spk2gender"
blacklisted_speakers_file = "blacklisted_speakers.txt"
blacklisted_sentences_file = "blacklisted_sentences.txt"



def parse_tsv(filename):
    print(filename)
    if os.path.exists(filename):
        speakers = set()
        sentences = set()
        vocabulary = set()
        num_m = 0
        act_num_m = 0 # Actual number of male speakers (as guessed by ear, in the file spk2gender)
        num_f = 0
        act_num_f = 0
        num_u = 0
        act_num_u = 0
        dur_m = 0.0
        act_dur_m = 0.0
        dur_f = 0.0
        act_dur_f = 0.0
        dur_u = 0.0
        
        # client_id, path, sentence, up_votes, down_votes, age, gender, accent
        with open(filename, 'r') as f:
            f.readline() # skip header
            l = f.readline().strip()
            while l:
                l = l.split('\t')
                speaker_id = l[0][:16]    # Shorten speaker-id
                if filtered_out:
                    if speaker_id in blacklisted_speakers or l[2] in blacklisted_sentences:
                        l = f.readline().strip()
                        continue
                
                duration = get_audiofile_length( os.path.join(clip_dir, l[1]) )
                if l[6] == "male":
                    if not speaker_id in speakers:
                        num_m += 1
                        act_num_m += 1
                    dur_m += duration
                    act_dur_m += duration
                elif l[6] == "female":
                    if not speaker_id in speakers:
                        num_f += 1
                        act_num_f += 1
                    dur_f += duration
                    act_dur_f += duration
                else:
                    dur_u += duration
                    if speaker_id in speakers:
                        if speaker_id in speakers_gender:
                            if speakers_gender[speaker_id] == 'm':
                                act_dur_m += duration
                            elif speakers_gender[speaker_id] == 'f':
                                act_dur_f += duration
                    else:
                        num_u += 1
                        if speaker_id in speakers_gender:
                            if speakers_gender[speaker_id] == 'm':
                                act_num_m += 1
                                act_dur_m += duration
                            elif speakers_gender[speaker_id] == 'f':
                                act_num_f += 1
                                act_dur_f += duration
                        else:
                            act_num_u += 1
                            print("unknown gender:", speaker_id)
                speakers.add(speaker_id)
                sentences.add(l[2])
                corrected, _ = get_cleaned_sentence(l[2])
                vocabulary.update(corrected.split())
                l = f.readline().strip()
        print("Number of speakers:", len(speakers))
        print("Number of sentences:", len(sentences))
        print("Vocabulary size:", len(vocabulary))
        total_length = dur_m + dur_f + dur_u
        minutes, seconds = divmod(round(total_length), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Audio length: {hours} h {minutes}'{seconds}''")
        print("--------")
        print(f"Male speakers: {num_m} ({round(100 * num_m/len(speakers), 2)}%)")
        print(f"Actual male speakers: {act_num_m} ({round(100 * act_num_m/len(speakers), 2)}%)")
        minutes, seconds = divmod(round(dur_m), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Male audio length: {hours} h {minutes}'{seconds}'' ({round(100 * dur_m/total_length, 2)}%)")
        minutes, seconds = divmod(round(act_dur_m), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Actual male audio length: {hours} h {minutes}'{seconds}'' ({round(100 * act_dur_m/total_length, 2)}%)")
        print("--------")
        print(f"Female speakers: {num_f} ({round(100 * num_f/len(speakers), 2)}%)")
        print(f"Actual female speakers: {act_num_f} ({round(100 * act_num_f/len(speakers), 2)}%)")
        minutes, seconds = divmod(round(dur_f), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Female audio length: {hours} h {minutes}'{seconds}'' ({round(100 * dur_f/total_length, 2)}%)")
        minutes, seconds = divmod(round(act_dur_f), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Actual female audio length: {hours} h {minutes}'{seconds}'' ({round(100 * act_dur_f/total_length, 2)}%)")
        print("--------")
        print(f"Unknown gender speakers: {num_u} ({round(100 * num_u/len(speakers), 2)}%)")
        print(f"Actual unk gender speakers: {act_num_u} ({round(100 * act_num_u/len(speakers), 2)}%)")
        minutes, seconds = divmod(round(dur_u), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"Unk gender audio length: {hours} h {minutes}'{seconds}'' ({round(100 * dur_u/total_length, 2)}%)")
        print("--------")
        print()
        return speakers, sentences, vocabulary
    else:
        print("File not found:", filename)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} data_file.tsv [data_file2.tsv...]")
        sys.exit(1)
    
    clip_dir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[1])), "clips")
    
    speakers_gender = dict()
    if os.path.exists(spk2gender_file):
        with open(spk2gender_file, 'r') as f:
            for l in f.readlines():
                speaker, gender = l.split()
                speakers_gender[speaker] = gender
    else:
        print("spk2gender file not found")
    
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
    
    speaker_list = []
    sentence_list = []
    vocabulary_list = []
    files = sys.argv[1:]    
    for file in files:
        speakers, sentences, vocabulary = parse_tsv(file)
        speaker_list.append(speakers)
        sentence_list.append(sentences)
        vocabulary_list.append(vocabulary)
    
    global_vocab = set()
    for vocab in vocabulary_list:
        global_vocab.update(vocab)
        
    
    print("Common speakers:", len(speaker_list[0].intersection(*speaker_list[1:])))
    print("Common sentences:", len(sentence_list[0].intersection(*sentence_list[1:])))
    print("Global vocabulary size:", len(global_vocab))
    intersecting_vocab = vocabulary_list[0].intersection(*vocabulary_list[1:])
    print(f"Intersecting vocabulary: {round(100 * len(intersecting_vocab) / len(global_vocab) ,2)}%")
    print("Size of intersecting vocab:", len(intersecting_vocab))
    
