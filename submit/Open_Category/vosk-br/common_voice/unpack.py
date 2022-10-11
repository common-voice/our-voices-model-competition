#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Author:        Gweltaz Duval-Guennoc
 
    Unpack Mozilla's Common Voice dataset and prepare data
    to be used for Kaldi framework.
    
    
    usage:
        $ python3 unpack.py train.tsv train
        $ python3 unpack.py test.tsv test
 
"""


import sys
import os
import tarfile
from math import floor, ceil
from pydub import AudioSegment

sys.path.append("..")
import libMySTT



spk2gender_file = "spk2gender"
blacklisted_speakers_file = "blacklisted_speakers.txt"
blacklisted_sentences_file = "blacklisted_sentences.txt"



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"usage: {sys.argv[0]} data_file.tsv [data_file2.tsv...] SAVE_FOLDER")
        sys.exit(1)
    
    tar_file = [f for f in os.listdir() if f.endswith(".tar.gz")][0]
    with tarfile.open(tar_file, 'r') as tar:
        data_folder = tar.getnames()[0]
        if not os.path.exists(data_folder):
            # Untar archive
            tar.extractall()
            #os.system("tar xvf cv-corpus-*-br.tar.gz")
    
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
            blacklisted_speakers = [l.split()[0] for l in f.readlines() if not l.startswith('#')]
    else:
        print("Blacklisted speakers file not found")
   
    blacklisted_sentences = []
    if os.path.exists(blacklisted_sentences_file):
        with open(blacklisted_sentences_file, 'r') as f:
            blacklisted_sentences = [l.strip() for l in f.readlines() if not l.startswith('#')]
    else:
        print("Blacklisted sentences file not found")
    
    dest_folder = sys.argv[-1]
    data_files = sys.argv[1:-1]
    
    clips_folder = os.path.join(data_folder, "clips")
    ungendered_speakers = set()
    parsed_audiofiles = set()   # To make sure every utterance is used only once in datasets
    
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)
    
    if not os.path.exists("discarded"):
        os.mkdir("discarded")
    
    for data_file in data_files:
        data = []
        cumul_time = 0
        
        data_file = os.path.join(data_folder, data_file)
        print(data_file)
        if os.path.exists(data_file):
            # client_id, path, sentence, up_votes, down_votes, age, gender, accent
            with open(data_file, 'r') as f:
                f.readline() # skip header
                l = f.readline().strip()
                while l:
                    l = l.split('\t')
                    l[0] = l[0][:16]    # Shorten speaker-id
                    data.append(l[:8])  # Keep first 8 fields only
                    l = f.readline().strip()
        else:
            print("File not found:", data_file)
            continue
        
        speakers = set([l[0] for l in data])
        print(f"{len(speakers)} speakers found...")
        
        for speaker in speakers:
            # for each speaker, create a folder an concatenate each of its utterances in one audio file
            discard = speaker in blacklisted_speakers
            if discard:
                print("(discarded)", end=' ')
            
            print(speaker, end=' ')
            
            utterances = [utt for utt in data if utt[0] == speaker]
            
            # Filter out gwenedeg from training data
            #if utterances[0][7] == "gwenedeg":
            #    print("gwenedeg (skipping)")
            #    continue
            
            if speaker in speakers_gender:
                print(f'[{speakers_gender[speaker]}]', end=' ')
            elif utterances[0][6] in ('female', 'male'):
                print(f'[{utterances[0][6][0]}]', end=' ')
                speakers_gender[speaker] = utterances[0][6][0]
            elif not discard:
                ungendered_speakers.add(speaker)
            
            if discard:
                speaker_folder = os.path.join("discarded", speaker)
            else:
                speaker_folder = os.path.join(dest_folder, speaker)
            
            if not os.path.exists(speaker_folder):
                os.mkdir(speaker_folder)
            else:
                # Speaker has already been parsed
                print('|')
                continue
            
            audiofiles = []
            text = []
            segments = []
            t = 0
            for utt in utterances:
                if utt[1] in parsed_audiofiles:
                    print("already seen:", utt)
                else:
                    parsed_audiofiles.add(utt[1])
                
                if utt[2] in blacklisted_sentences:
                    print("\nskipped:", utt[2])
                    continue
                
                wav = utt[1].replace('.mp3', '.wav')
                src = os.path.join(clips_folder, utt[1])
                dst = os.path.join(speaker_folder, wav)
                # Convert to wav
                if not os.path.exists(dst):
                    libMySTT.convert_to_wav(src, dst, verbose=False)
                #os.remove(src)
                nt = t + libMySTT.get_audiofile_length(dst)*1000
                segments.append((floor(t), ceil(nt) + 200)) # Offset end of segment by a 0.2 second
                t = nt
                audiofiles.append(dst)
                text.append(utt[2])
                print('.', end='')
                sys.stdout.flush()
            
            if not discard:
                cumul_time += t
            
            # Text file
            with open(os.path.join(speaker_folder, speaker+".txt"), "w") as f:
                f.write(f"{{{speaker}}}\n")
                f.write('\n'.join(text))
            
            # Split file
            with open(os.path.join(speaker_folder, speaker+".split"), "w") as f:
                for delim in segments:
                    f.write(f"{delim[0]} {delim[1]}\n")
            
            # Concatenate audio files of the same speaker
            out_filename = os.path.join(speaker_folder, speaker+'.wav')
            if len(audiofiles) == 1:
                os.rename(audiofiles[0], out_filename)
            elif not os.path.exists(out_filename):
                libMySTT.concatenate_audiofiles(audiofiles, out_filename)
            
            print('|')
    
        minutes, seconds = divmod(round(cumul_time/1000), 60)
        hours, minutes = divmod(minutes, 60)
        print(f"total clip time kept : {hours}h {minutes}' {seconds}''")
    
    
    # Categorise speakers of unknown gender
    # (this will help us measure the gender bias more precisely later)
    for speaker in ungendered_speakers:
        speaker_folder = os.path.join(dest_folder, speaker)
        split_file = os.path.join(speaker_folder, speaker+".split")
        segments = libMySTT.load_segments(split_file)
        wav_filename = os.path.join(speaker_folder, speaker+'.wav')
        song = AudioSegment.from_wav(wav_filename)
        gender = ''
        i = 0
        while gender not in ('m', 'f', 'u', 'x'):
            libMySTT.play_segment(i, song, segments, 1.0)
            print("(Press 'u' for unknown, 'x' to skip this process or any other key to listen again)")
            gender = input(f"{speaker} Male or Female (m/f) ? ").lower()
            i = (i+1) % len(segments)
            if gender in ('m', 'f'):
                speakers_gender[speaker] = gender
        
        if gender == 'x':
            break
        
    
    # spk2gender file
    previous_speakers = []
    if os.path.exists(spk2gender_file):
        with open(spk2gender_file, 'r') as f:
            previous_speakers = [l.split()[0] for l in f.readlines()]
    
    with open(spk2gender_file, 'a') as f:
        for speaker in speakers_gender:
            if speaker not in previous_speakers:
                f.write(f"{speaker}\t{speakers_gender[speaker]}\n") 
