#! /usr/bin/env python3


"""
    Build a text file and a wave audio file from a list of split files and a specified gender
    
    Usage : ./split_by_gender.py folder
"""

import sys
import os
from pydub import AudioSegment
from libMySTT import load_segments, get_cleaned_sentence, list_files_with_extension, SPEAKER_ID_PATTERN
from math import floor, ceil



gender = 'f'
output_dir = "gender_filtered"

MAKE_GLOBAL_AUDIO_AND_TEXT_FILE = True



def parse_file(split_filename):
    recording_id = os.path.basename(split_filename).split(os.path.extsep)[0]
    print(f"== {recording_id} ==")
    text_filename = split_filename.replace('.split', '.txt')
    assert os.path.exists(text_filename), f"ERROR: no text file found for {recording_id}"
    
    f_segments = []
    f_text = []
    m_segments = []
    m_text = []

    segments = load_segments(split_filename)
    
    speaker_id = "unnamed"
    with open(text_filename, 'r') as f:
        idx = 0
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
                
                start, end = speaker_id_match.span()
                l = l[:start] + l[end:]
                l = l.strip()
            
            cleaned = get_cleaned_sentence(l)[0]      
            if cleaned:
                cleaned = cleaned.replace('*', '')
                s = segments[idx]
                s = (s[0], s[1]-100)
                
                if speakers_gender[speaker_id] == 'f':
                    f_text.append(cleaned)
                    f_segments.append(s)
                elif speakers_gender[speaker_id] == 'm':
                    m_text.append(cleaned)
                    m_segments.append(s)
                
                idx += 1
    
    return f_segments, f_text, m_segments, m_text


if __name__ == "__main__":
    # Add external speakers gender
    speakers_gender = {}
    for fname in ["spk2gender.txt", "common_voice/spk2gender"]:
        if os.path.exists(fname):
            print(f"Adding speakers from '{fname}'")
            with open(fname, 'r') as f:
                for l in f.readlines():
                    spk, gender = l.strip().split()
                    speakers_gender[spk] = gender

    if len(sys.argv) == 2:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        
        silence = AudioSegment.silent(duration=500)
        rep = sys.argv[1]
        split_files = list_files_with_extension('.split', rep)
        
        fsong = AudioSegment.empty()
        msong = AudioSegment.empty()
        ftext = []
        mtext = []
        f_audio_length = 0.0
        m_audio_length = 0.0

        for filename in split_files:
            f_segments, f_text, m_segments, m_text = parse_file(filename)
            ftext.extend(f_text)
            mtext.extend(m_text)

            wav_filename = filename.replace('.split', '.wav')
            assert os.path.exists(wav_filename), f"ERROR: no wave file found for {filename}"
            song = AudioSegment.from_wav(wav_filename)
            
            for seg in f_segments:
                fsong += song[seg[0]:seg[1]]
                fsong += silence
                f_audio_length += (seg[1] / 1000) - (seg[0] / 1000)
            for seg in m_segments:
                msong += song[seg[0]:seg[1]]
                msong += silence
                m_audio_length += (seg[1] / 1000) - (seg[0] / 1000)
            
        fsong.export(os.path.join(output_dir, "audio_f.wav"), format="wav")
        msong.export(os.path.join(output_dir, "audio_m.wav"), format="wav")
        
        if MAKE_GLOBAL_AUDIO_AND_TEXT_FILE:
            all_audio = fsong + msong
            all_audio.export(os.path.join(output_dir, "audio_all.wav"), format="wav")
            all_text = ftext + mtext
            with open(os.path.join(output_dir, "text_all.txt"), 'w') as f:
                f.writelines([l + '\n' for l in all_text])
        
        with open(os.path.join(output_dir, "text_f.txt"), 'w') as f:
            f.writelines([l + '\n' for l in ftext])
        with open(os.path.join(output_dir, "text_m.txt"), 'w') as f:
            f.writelines([l + '\n' for l in mtext])
        
        total_audio_length = f_audio_length + m_audio_length
        minutes, seconds = divmod(round(f_audio_length), 60)
        hours, minutes = divmod(minutes, 60)
        pc = round(100*f_audio_length/total_audio_length)
        print(f"- Female speakers:\t{hours} h {minutes}'{seconds}''\t{pc}%")
        minutes, seconds = divmod(round(m_audio_length), 60)
        hours, minutes = divmod(minutes, 60)
        pc = round(100*m_audio_length/total_audio_length)
        print(f"- Male speakers:\t{hours} h {minutes}'{seconds}''\t{pc}%")
        
    else:
        print("folder name missing")

