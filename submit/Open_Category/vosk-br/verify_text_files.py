#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File:       verify_text_files.py
    
    Check spelling in every text file in folder and subfolders
    Prompt for new found acronyms
    
    
    Author:     Gweltaz Duval-Guennoc
 
"""


import sys
import os
import re
import libMySTT
from colorama import Style



def get_text_files(root):
    textfiles = []
    for dirpath, dirs, files in os.walk(root):
        for name in files:
            if name in ["notes.txt"]:
                continue
            if name.endswith('.txt'):
                textfiles.append(os.path.join(dirpath, name))
    return textfiles
    


if __name__ == "__main__":
    textfiles = get_text_files(sys.argv[1])
    
    num_errors = 0
    for file in textfiles:
        split_filename = file.replace('.txt', '.split')
        if not os.path.exists(split_filename):
            continue
        with open(file, 'r') as f:
            print(file)
            num_line = 0
            for line in f.readlines():
                num_line += 1
                # Remove speaker tag
                speaker_id_match = libMySTT.SPEAKER_ID_PATTERN.search(line)
                if speaker_id_match:
                    #speaker_id = speaker_id_match[1]
                    start, end = speaker_id_match.span()
                    line = line[:start] + line[end:]
                
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    continue
                    
                correction, errors = libMySTT.get_correction(line)
                num_errors += errors
                if errors:
                    print(f"[{num_line}] {correction}")
                    print(f"{Style.DIM}[{line.strip()}]{Style.RESET_ALL}")
        
            # extract acronyms
            extracted_acronyms = libMySTT.extract_acronyms_from_file(file)
            if extracted_acronyms:
                with open(libMySTT.ACRONYM_PATH, 'a') as f:
                    for acr in extracted_acronyms:
                        f.write(f"{acr} {extracted_acronyms[acr]}\n")
                        libMySTT.acronyms[acr] = extracted_acronyms[acr]
                        num_errors -= 1
    
    print(f"{num_errors} spelling mistakes")
