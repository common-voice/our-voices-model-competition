#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Build necessary kaldi files to train an ASR model from audio an textual data
 
 Author:  Gweltaz Duval-Guennoc
 
 Notes: 
 
"""


import sys
import os
import numpy as np
import re
from math import floor, ceil
from libMySTT import *


BUILD_ML_CORPUS = True
ADD_EXTERNAL_CORPUS_TO_ML = 'corpus/wiki_corpus_big.txt'     # Add a corpus from wikipedia

SENTENCE_MIN_WORDS = 0

spk2gender_files = ["spk2gender.txt", "common_voice/spk2gender"]



def parse_rep(rep):
    split_files = []
    for filename in os.listdir(rep):
        if filename.lower().endswith('.split'):
            split_files.append(os.path.join(rep, filename))
    
    wavscp = []
    text = []
    segments = []
    utt2spk = []
    
    for f in split_files:
        recording_id, wav_filename, text_data, segments_data, utt2spk_data = parse_data(f)
        wavscp.append((recording_id, os.path.abspath(wav_filename)))
        text.extend(text_data)
        segments.extend(segments_data)
        utt2spk.extend(utt2spk_data)
    
    return wavscp, text, segments, utt2spk
    

def parse_data(split_filename):
    recording_id = os.path.basename(split_filename).split(os.path.extsep)[0]
    print(f"== {recording_id} ==")
    text_filename = split_filename.replace('.split', '.txt')
    assert os.path.exists(text_filename), f"ERROR: no text file found for {recording_id}"
    wav_filename = split_filename.replace('.split', '.wav')
    assert os.path.exists(wav_filename), f"ERROR: no wave file found for {recording_id}"
    
    make_corpus = True
    corpus_filename = os.path.abspath(os.path.join(rep, recording_id + '.cor'))
    if os.path.exists(corpus_filename):
        make_corpus = False
    
    text = []
    speaker_ids = []
    speaker_id = "unnamed"
    with open(text_filename, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            if not l or l.startswith('#'):
                continue
            
            # Extract speaker id
            speaker_id_match = SPEAKER_ID_PATTERN.search(l)
            if speaker_id_match:
                speaker_id = speaker_id_match[1].lower()
                speaker_gen = speaker_id_match[2]
                if speaker_id not in speakers_gender:
                    if "paotr" in speaker_id:
                        speakers_gender[speaker_id] = 'm'
                    elif "plach" in speaker_id:
                        speakers_gender[speaker_id] = 'f'
                    else:
                        speakers_gender[speaker_id] = speaker_gen
                else:
                    if not speakers_gender[speaker_id] and speaker_gen:
                        speakers_gender[speaker_id] = speaker_gen.lower()
                
                speakers.add(speaker_id)
                start, end = speaker_id_match.span()
                l = l[:start] + l[end:]
                l = l.strip()
            
            cleaned = get_cleaned_sentence(l)[0]      
            if cleaned:
                speaker_ids.append(speaker_id)
                text.append(cleaned.replace('*', ''))
                
                # Add words to lexicon
                for w in cleaned.split():
                    # Remove black-listed words (beggining with '*')
                    if w.startswith('*'):
                        pass
                    elif w in verbal_tics:
                        pass
                    elif is_acronym(w):
                        pass
                    elif w.lower() in capitalized:
                        pass
                    else: regular_words.add(w)
            
            # Add sentences to corpus
            if make_corpus:
                for sentence in l.split('.'):
                    if not sentence:
                        continue
                    cleaned, bl_score = get_cleaned_sentence(sentence, rm_bl_marker=True, rm_verbal_ticks=True)
                    if not cleaned:
                        continue
                    # Ignore if to many black-listed words in sentence
                    if bl_score > 0.2:
                        #correction, _ = get_correction(sentence)
                        #print(f"rejected ({bl_score}): {correction}")
                        print("rejectd", cleaned)
                        continue
                    
                    # Ignore of sentence is too short
                    if cleaned.count(' ') < SENTENCE_MIN_WORDS - 1:
                        print("corpus skip:", cleaned)
                        continue
                    
                    corpus.add(cleaned)
    
    if not make_corpus:
        with open(corpus_filename, 'r') as f:
            for l in f.readlines():
                corpus.add(l.strip())
     
    segments = load_segments(split_filename)
    assert len(text) == len(segments), \
        f"number of utterances in text file ({len(text)}) doesn't match number of segments in split file ({len(segments)})"

    segments_data = []
    text_data = []
    utt2spk_data = []
    for i, s in enumerate(segments):
        start = s[0] / 1000
        stop = s[1] / 1000
        speaker_gender = 'u'
        if speaker_ids[i] in speakers_gender:
            speaker_gender = speakers_gender[speaker_ids[i]]
        else:
            print("unknown gender:", speaker_ids[i])
        
        if speaker_gender == 'm':
            global male_audio_length
            male_audio_length += stop - start
        elif speaker_gender == 'f':
            global female_audio_length
            female_audio_length += stop - start
            
        utterance_id = f"{speaker_ids[i]}-{recording_id}-{floor(100*start):0>7}_{ceil(100*stop):0>7}"
        text_data.append((utterance_id, text[i]))
        segments_data.append(f"{utterance_id}\t{recording_id}\t{floor(start*100)/100}\t{ceil(stop*100)/100}\n")
        utt2spk_data.append(f"{utterance_id}\t{speaker_ids[i]}\n")
    
    print()
    return recording_id, wav_filename, text_data, segments_data, utt2spk_data



if __name__ == "__main__":
    rep = ""
    wavscp = []
    text = []
    segments = []
    utt2spk = []
    regular_words = set()
    speakers = set()
    corpus = set()
    speakers_gender = {}
    male_audio_length = 0.0
    female_audio_length = 0.0
    
    # Add external speakers gender
    for fname in spk2gender_files:
        if os.path.exists(fname):
            print(f"Adding speakers from '{fname}'")
            with open(fname, 'r') as f:
                for l in f.readlines():
                    spk, gender = l.strip().split()
                    speakers_gender[spk] = gender
    
    if os.path.isdir(sys.argv[1]):
        rep = sys.argv[1]
        for filename in os.listdir(rep):
            filename = os.path.join(rep, filename)
            if os.path.isdir(filename):
                wavscp_data, text_data, segments_data, utt2spk_data = parse_rep(filename)
                wavscp.extend(wavscp_data)
                text.extend(text_data)
                segments.extend(segments_data)
                utt2spk.extend(utt2spk_data)
            elif filename.endswith('.split'):   # Folder with a single data item
                recording_id, wav_filename, text_data, segments_data, utt2spk_data = parse_data(filename)
                wavscp.append((recording_id, os.path.abspath(wav_filename)))
                text.extend(text_data)
                segments.extend(segments_data)
                utt2spk.extend(utt2spk_data)
                break
                
    else:
        print("Argument should be a directory")
        sys.exit(1)
            
    if not os.path.exists('data'):
        os.mkdir('data')
    
    if not os.path.exists(os.path.join('data', 'local')):
        os.mkdir(os.path.join('data', 'local'))
        
        # External text corpus will be added now
        if BUILD_ML_CORPUS and ADD_EXTERNAL_CORPUS_TO_ML and os.path.exists(ADD_EXTERNAL_CORPUS_TO_ML):
            print("parsing and copying external corpus")
            with open('data/local/corpus.txt', 'w') as fw:
                with open(ADD_EXTERNAL_CORPUS_TO_ML, 'r') as fr:
                    for sentence in fr.readlines():
                        cleaned = get_cleaned_sentence(sentence)[0]
                        for word in cleaned.split():
                            if word.lower() in regular_words:
                                pass
                            elif word.lower() in capitalized:
                                pass
                            elif is_acronym(word) and word in acronyms:
                                pass
                            else:
                                regular_words.add(word)
                        fw.write(cleaned + '\n')
        
    dict_dir = os.path.join('data', 'local', 'dict_nosp')
    if not os.path.exists(dict_dir):
        os.mkdir(dict_dir)
    
    save_dir = os.path.join('data', os.path.split(os.path.normpath(rep))[1])
    #save_dir = os.path.abspath(save_dir)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
        
    
    # Build 'text' file
    fname = os.path.join(save_dir, 'text')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        for l in text:
            f.write(f"{l[0]}\t{l[1]}\n")
    
    # Build 'segments' file
    fname = os.path.join(save_dir, 'segments')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        f.writelines(segments)
    
    # Build 'utt2spk'
    fname = os.path.join(save_dir, 'utt2spk')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        f.writelines(utt2spk)
    
    # Build 'spk2gender'
    fname = os.path.join(save_dir, 'spk2gender')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        for speaker in sorted(speakers):
            f.write(f"{speaker}\t{speakers_gender[speaker]}\n")
    
    # Build 'wav.scp'
    fname = os.path.join(save_dir, 'wav.scp')
    print(f"building file {fname}")
    with open(fname, 'w') as f:
        for rec_id, wav_filename in wavscp:
            f.write(f"{rec_id}\t{wav_filename}\n")
    
    # Lexicon.txt
    # If a lexicon is already present in folder (i.e. this script has already been
    # run on anoter set), it will be merged with the current lexicon.
    # The lexicons of the train and test sets are thus merged together.
    # Right now the lexicon is build irrespective of the corpus, which is not optimal
    lexicon_path = os.path.join(dict_dir, 'lexicon.txt')
    if os.path.exists(lexicon_path):
        print('lexicon.txt file already exists')
        old_lexicon = set()
        with open(lexicon_path, 'r') as f:
            for l in f.readlines()[3:]:
                old_lexicon.add(l.split()[0])
        with open(lexicon_path, 'a') as f:
            for w in sorted(regular_words):
                if not w in old_lexicon:
                    f.write(f"{w} {' '.join(word2phonetic(w))}\n")
    else:    
        print(f"building file {lexicon_path}")
        lexicon = []
        for w in sorted(regular_words):
            lexicon.append(f"{w} {' '.join(word2phonetic(w))}")
        with open(LEXICON_ADD_PATH, 'r') as f_in:
            for l in f_in.readlines():
                lexicon.append(l.strip())
        for w in acronyms:
            for pron in acronyms[w]:
                lexicon.append(f"{w} {pron}")
        for w in capitalized:
            for pron in capitalized[w]:
                lexicon.append(f"{w.capitalize()} {pron}")
        for w in verbal_tics:
            lexicon.append(f"{w} {verbal_tics[w]}")
        
        with open(lexicon_path, 'w') as f_out:
            f_out.write(f"!SIL SIL\n<SPOKEN_NOISE> SPN\n<UNK> SPN\n")
            for line in lexicon:
                f_out.write(line + '\n')
            
    
    # nonsilence_phones.txt
    print('building file data/local/dict_nosp/nonsilence_phones.txt')
    with open('data/local/dict_nosp/nonsilence_phones.txt', 'w') as f:
        for p in sorted(phonemes):
            f.write(f'{p}\n')
    
    # silence_phones.txt
    print('building file data/local/dict_nosp/silence_phones.txt')
    with open('data/local/dict_nosp/silence_phones.txt', 'w') as f:
        f.write(f'SIL\noov\nSPN\n')
    
    # optional_silence.txt
    print('building file data/local/dict_nosp/optional_silence.txt')
    with open('data/local/dict_nosp/optional_silence.txt', 'w') as f:
        f.write('SIL\n')
    
    # Copy text corpus
    if BUILD_ML_CORPUS:
        with open('data/local/corpus.txt', 'a') as f_out:
            for l in corpus:
                f_out.write(f"{l}\n")
    
    print()
    print("==== STATS ====")
    total_audio_length = male_audio_length + female_audio_length
    minutes, seconds = divmod(round(total_audio_length), 60)
    hours, minutes = divmod(minutes, 60)
    print(f"- Total audio length:\t{hours} h {minutes}'{seconds}''")
    minutes, seconds = divmod(round(male_audio_length), 60)
    hours, minutes = divmod(minutes, 60)
    pc = round(100*male_audio_length/total_audio_length)
    print(f"- Male speakers:\t{hours} h {minutes}'{seconds}''\t{pc}%")
    minutes, seconds = divmod(round(female_audio_length), 60)
    hours, minutes = divmod(minutes, 60)
    pc = round(100*female_audio_length/total_audio_length)
    print(f"- Female speakers:\t{hours} h {minutes}'{seconds}''\t{pc}%")
