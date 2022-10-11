#! /usr/bin/env python3
# -*- coding: utf-8 -*-


"""
 Common functions for audio file playback and data parsing
 
 Author:  Gweltaz Duval-Guennoc

"""


import os
import json
import re
from pydub import AudioSegment
#from pydub.playback import play
from pydub.utils import get_player_name
from tempfile import NamedTemporaryFile
import subprocess
import hunspell # https://www.systutorials.com/docs/linux/man/4-hunspell/
from colorama import Fore



ROOT = os.path.dirname(os.path.abspath(__file__))

HS_DIC_PATH = os.path.join(ROOT, os.path.join("hunspell-dictionary", "br_FR"))
#HS_AFF_PATH = os.path.join(ROOT, os.path.join("hunspell-dictionary", "br_FR.aff"))
HS_ADD_PATH= os.path.join(ROOT, os.path.join("hunspell-dictionary", "add.txt"))

CORRECTED_PATH = os.path.join(ROOT, "corrected.txt")
CAPITALIZED_PATH = os.path.join(ROOT, "capitalized.txt")
JOINED_PATH = os.path.join(ROOT, "joined.txt")
ACRONYM_PATH = os.path.join(ROOT, "acronyms.txt")
LEXICON_ADD_PATH = os.path.join(ROOT, "lexicon_add.txt")
LEXICON_REPLACE_PATH = os.path.join(ROOT, "lexicon_replace.txt")

SPEAKER_ID_PATTERN = re.compile(r'{([-\w]+):*([mf])*}')


verbal_tics = {
    'euh'   :   'OE',
    'euhm'  :   'OE M',
    'beñ'   :   'B EN',
    'eba'   :   'E B A',
    'ebeñ'  :   'E B EN',
    'kwa'   :   'K W A',
    'heñ'   :   'EN',
    'boñ'   :   'B ON',
    'bah'   :   'B A',
    'feñ'   :   'F EN',
    'tieñ'  :   'T I EN',
    'alors' :   'A L OH R',
    'allez' :   'A L E',
    #'oh'    :   'O',
    #'ah'    :   'A',
}


#punctuation = (',', '.', ';', '?', '!', ':', '«', '»', '"', '”', '“', '(', ')', '…', '–', '‚')
punctuation = ',.;?!:«»"”“()…–‚'

valid_chars = "aâbcdeêfghijklmnñoprstuüùûvwyz'- "


w2f = {
    'a'     :   'A',
    'â'     :   'A',        # lÂret
    'añ'    :   'AN',
    'an'    :   'AN N',
    'b'     :   'B',
    'd'     :   'D',
    'ch'    :   'CH',       # CHomm
    "c'h"   :   'X',        # 
    'c'     :   'K',        # xxx GALLEG XXX
    'e'     :   'E',        # spErEd
    'ê'     :   'E',        # gÊr
    'é'     :   'E',        # xxx GALLEG XXX
    "ec'h"  :   'EH X',     # nec'h
    'ei'    :   'EY',       # kEIn      # could replace with (EH I) maybe ?
    'eiñ'   :   'EY',       # savetEIÑ
    'el.'   :   'EH L',     # broadEL
    'ell'   :   'EH L',
    'em'    :   'EH M',     # lEMm
    'eñ'    :   'EN',       # chEÑch
    'en.'   :   'EH N',     # meriEN
    'enn'   :   'EH N',     # lENN
    'er.'   :   'EH R',     # hantER
    'eu'    :   'EU',       # lEUn
    'eü'    :   'E U',      # EÜrus
    'euñv'  :   'EN',       # stEUÑV
    'f'     :   'F',
    'g'     :   'G',
    'gn'    :   'GN',       # miGNon
    'h'     :   'H',
    'ha.'   :   'A',
    'hag.'  :   'A G',
    'i'     :   'I',
    'iñ'    :   'I N',      # bIÑs
    'iñ.'   :   'I',        # debrIÑ
    'j'     :   'J',        # BeaJiñ
    'k'     :   'K',
    'l'     :   'L',
    'lh'    :   'LH',
    'll'    :   'L',
    'm'     :   'M',
    'mm'    :   'M',
    'n'     :   'N',
    'nn'    :   'N',
    'o'     :   'O',        # nOr
    'ô'     :   'O',        # kornôg
    'on'    :   'ON N',     # dON
    'ont.'  :   'ON N',     # mONt
    'oñ'    :   'ON',       # sOÑjal
    'ou'    :   'OU',       # dOUr
    'oû'    :   'OU',       # gOÛt (kerneveg)
    'où'    :   'OU',       # goulOÙ
    'or'    :   'OH R',     # dORn      ! dor, goudoriñ
    'orr'   :   'O R',      # gORRe
    'p'     :   'P',
    ".p'h"  :   'P',        # P'He
    'qu'    :   'K',        # xxx GALLEG XXX
    'r'     :   'R',
    'rr'    :   'R',
    's'     :   'S',
    't'     :   'T',
    'û'     :   'U',        # Ûioù (kerneveg)
    'u'     :   'U',        # tUd
    'uñ'    :   'UN',       # pUÑs
    '.un.'  :   'OE N',     # UN dra
    '.ul.'  :   'OE L',     # UL labous
    '.ur.'  :   'OE R',     # UR vag
    "'un."  :   'OE N',     # d'UN
    "'ur."  :   'OE R',     # d'UR
    "'ul."  :   'OE L',     # d'UL
    'v'     :   'V',
    'v.'    :   'O',        # beV
    'vr.'   :   'OH R',     # kaVR, loVR
    'w'     :   'W',
    'y'     :   'I',        # pennsYlvania
    'ya'    :   'IA',       # YAouank
    'ye'    :   'IE',       # YEzh
    'yo'    :   'IO',       # YOd
    'you'   :   'IOU',      # YOUc'hal
    'z'     :   'Z',
    'zh'    :   'Z',
}

acr2f = {
    'A' :   'A',
    'B' :   'B E',
    'C' :   'S E',
    'D' :   'D E',
    'E' :   'EU',
    'F' :   'EH F',
    'G' :   'J E',
    'H' :   'A CH',
    'I' :   'I',
    'J' :   'J I',
    'K' :   'K A',
    'L' :   'EH L',
    'M' :   'EH M',
    'N' :   'EH N',
    'O' :   'O',
    'P' :   'P E',
    'Q' :   'K U',
    'R' :   'EH R',
    'S' :   'EH S',
    'T' :   'T E',
    'U' :   'U',
    'V' :   'V E',
    'W' :   'OU E',
    'X' :   'I K S',
    
    'Z' :   'Z EH D',
}


phonemes = set()
for val in list(w2f.values()) + list(acr2f.values()) + list(verbal_tics.values()):
    for tok in val.split():
        phonemes.add(tok)



lexicon_rep = dict()
with open(LEXICON_REPLACE_PATH, 'r') as f:
    for l in f.readlines():
        w, *phon = l.split()
        lexicon_rep[w] = phon
        


def word2phonetic(word):
    if word in lexicon_rep:
        return lexicon_rep[word]
    
    head = 0
    phonemes = []
    word = '.' + word.strip().lower().replace('-', '.') + '.'
    error = False
    while head < len(word):
        parsed = False
        for i in (4, 3, 2, 1):
            token = word[head:head+i].lower()
            if token in w2f:
                phonemes.append(w2f[token])
                head += i-1
                parsed = True
                break
        head += 1
        if not parsed and token not in ('.', "'"):
            error = True
    
    if error:
        print("ERROR: word2phonetic", word, ' '.join(phonemes))
    
    return phonemes



def get_hunspell_dict():
    #hs = hunspell.HunSpell(HS_DIC_PATH, HS_AFF_PATH)
    hs = hunspell.Hunspell(HS_DIC_PATH) # for cyhunspell
    with open(HS_ADD_PATH, 'r') as f:
        for w in f.readlines():
            hs.add(w.strip())
    for w in verbal_tics:
        hs.add(w)
    for w in lexicon_rep.keys():
        hs.add(w)
    return hs

hs_dict = get_hunspell_dict()



def get_corrected_dict():
    corrected = dict()
    corrected_sentences = dict()
    corrected_sentences["&ltbr&gt"] = "" # Special rule for sentences comming from wikipedia
    
    with open(CORRECTED_PATH, 'r') as f:
        for l in f.readlines():
            #l = l.strip()
            if not l.strip() or l.startswith('#'):
                continue
            k, v = l.replace('\n', '').split('\t')
            v = v.replace('-', ' ')
            #k = k.lower()
            if ' ' in k:
                corrected_sentences[k] = v
            else:
                corrected[k.lower()] = v
    return corrected, corrected_sentences

corrected, corrected_sentences = get_corrected_dict()



def get_capitalized_dict():
    """
        Returns a set of lower case names (that should be capitalized)
    """
    capitalized = dict()
    with open(CAPITALIZED_PATH, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            w, *pron = l.strip().split()
            if not pron:
                pron = word2phonetic(w)
            if w.lower() in capitalized:
                capitalized[w.lower()].append(' '.join(pron))
            else:
                capitalized[w.lower()] = [' '.join(pron)]
    return capitalized

capitalized = get_capitalized_dict()



def get_acronyms_dict():
    """
        Acronyms are stored in UPPERCASE in dictionary
    """
    acronyms = dict()
    for l in "BDFGHIJKLMPQRSTUVWXZ":
        acronyms[l] = [acr2f[l]]
    
    if os.path.exists(ACRONYM_PATH):
        with open(ACRONYM_PATH, 'r') as f:
            for l in f.readlines():
                if l.startswith('#') or not l: continue
                acr, *pron = l.split()
                if acr in acronyms:
                    acronyms[acr].append(' '.join(pron))
                else:
                    acronyms[acr] = [' '.join(pron)]
    else:
        print("Acronym dictionary not found... creating file")
        open(ACRONYM_PATH, 'a').close()
    return acronyms

acronyms = get_acronyms_dict()



def filter_out(text, symbols):
    new_text = ""
    for l in text:
        if not l in symbols: new_text += l
    return ' '.join(new_text.split()) # Prevent multi spaces



def is_acronym(word):
    if len(word) < 2:
        return False
    valid = False
    for l in word:
        if l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            valid = True
            continue
        if l not in "-0123456789":
            return False
    return valid



def tokenize(sentence):
    sentence = filter_out(sentence, punctuation)
    sentence = sentence.replace('‘', "'")
    sentence = sentence.replace('’', "'")
    sentence = sentence.replace('ʼ', "'")
    sentence = sentence.replace('-', ' ')   # Split words like "sav-heol"
    sentence = sentence.replace('/', ' ')
    sentence = sentence.replace('|', ' ')
    tokens = []
    for t in sentence.split():
        if t.startswith("'"):
            tokens.append(t[1:])
        elif t.endswith("'"):
            tokens.append(t[:-1])
        else:
            tokens.append(t) 
    return tokens



def get_cleaned_sentence(sentence, rm_bl_marker=False, rm_verbal_ticks=False):
    """
        Return a cleaned sentence, proper to put in text files or corpus
               and a quality score (ratio of black-listed words, the lower the better)
    """
    if not sentence:
        return '', 0
    
    lowered_sentence = sentence.lower()
    for mistake in corrected_sentences.keys():
        if mistake in sentence or mistake in lowered_sentence:
            sentence = sentence.replace(mistake, corrected_sentences[mistake]) # Won't work if mistake is capitalized in original sentence
    
    tokens = []
    num_blacklisted = 0
    for token in tokenize(sentence):
        lowered_token = token.lower()
        # Ignore black listed words
        if token.startswith('*'):
            if rm_bl_marker:
                tokens.append(token[1:])
            else:
                tokens.append(token)
            num_blacklisted += 1
        elif rm_verbal_ticks and lowered_token in verbal_tics:
            pass
        elif lowered_token in corrected:
            tokens.append(corrected[lowered_token])
        elif lowered_token in capitalized:
            tokens.append(token.capitalize())
        elif is_acronym(token):
            tokens.append(token)
            if not token in acronyms:
                num_blacklisted += 1
        else:
            tokens.append(lowered_token)
    if not tokens:
        return '', 1
    return ' '.join(tokens), float(num_blacklisted)/len(tokens)



def get_correction(sentence):
    """
        Return a string which is a colored correction of the sentence
        and the number of spelling mistakes in sentence
    """
    
    sentence = sentence.strip()
    if not sentence:
        return ''
    
    lowered_sentence = sentence.lower()
    for mistake in corrected_sentences.keys():
        if mistake in sentence or mistake in lowered_sentence:
            sentence = sentence.replace(mistake, corrected_sentences[mistake])
    
    num_errors = 0
    tokens = []
    for token in tokenize(sentence):
        spell_error = False
        lowered_token = token.lower()
        # Ignore black listed words
        if token.startswith('*'):
            tokens.append(Fore.YELLOW + token + Fore.RESET)
        elif lowered_token in verbal_tics:
            tokens.append(Fore.YELLOW + token + Fore.RESET)
        elif lowered_token in corrected:
            tokens.append(Fore.GREEN + corrected[lowered_token] + Fore.RESET)
        elif token.isdigit():
            spell_error = True
            tokens.append(Fore.RED + token + Fore.RESET)
            
        # Check for hyphenated words
        
        elif is_acronym(token):
            if token in acronyms:
                tokens.append(Fore.BLUE + token + Fore.RESET)
            else:
                tokens.append(Fore.RED + token + Fore.RESET)
                spell_error = True
        elif lowered_token in capitalized:
            tokens.append(token.capitalize())
        elif not hs_dict.spell(token):
            spell_error = True
            tokens.append(Fore.RED + token + Fore.RESET)
        else:
            tokens.append(lowered_token)
        
        if spell_error:
            num_errors += 1
        
    return ' '.join(tokens), num_errors



def prompt_acronym_phon(w, song, segments, idx):
    """
        w: Acronym
        i: segment number in audiofile (from 'split' file) 
    """
    
    guess = ' '.join([acr2f[l] for l in w if l in acr2f])
    print(f"Phonetic proposition for '{w}' : {guess}")
    while True:
        answer = input("Press 'y' to validate, 'l' to listen, 'x' to skip or write a different prononciation: ").strip().upper()
        if not answer:
            continue
        if answer == 'X':
            return None
        if answer == 'Y':
            return guess
        if answer == 'L':
            play_segment(idx, song, segments, 1.5)
            continue
        valid = True
        for phoneme in answer.split():
            if phoneme not in phonemes:
                print("Error : phoneme not in", ' '.join(phonemes))
                valid = False
        if valid :
            return answer



def extract_acronyms(text):
    extracted = set()
    for w in tokenize(text):
        # Remove black-listed words (beggining with '*')
        if w.startswith('*'):
            continue
        if is_acronym(w):
            extracted.add(w)
    
    return list(extracted)



def extract_acronyms_from_file(text_filename):
    split_filename = text_filename[:-3] + 'split'
    segments = load_segments(split_filename)
    
    wav_filename = text_filename[:-3] + 'wav'
    song = AudioSegment.from_wav(wav_filename)
    
    extracted_acronyms = dict()
    
    with open(text_filename, 'r') as f:
        sentence_idx = 0
        for l in f.readlines():
            l = l.strip()
            if not l:
                continue
            if l.startswith('#'):
                continue
            
            l, _ = get_cleaned_sentence(l)
            
            speaker_id_match = SPEAKER_ID_PATTERN.search(l)
            if speaker_id_match:
                #current_speaker = speaker_id_match[1]
                start, end = speaker_id_match.span()
                l = l[:start] + l[end:]
            l = l.strip()
            if not l:   # In case the speaker pattern is the only text on the line
                continue
            
            for acr in extract_acronyms(l):
                if not acr in acronyms and not acr in extracted_acronyms:
                    print(sentence_idx)
                    
                    phon = prompt_acronym_phon(acr, song, segments, sentence_idx)
                    if phon:
                        extracted_acronyms[acr] = phon
            sentence_idx += 1
    
    return extracted_acronyms



def load_segments(filename):
    segments = []
    with open(filename, 'r') as f:
        for l in f.readlines():
            l = l.strip()
            if l:
                t = l.split()
                start = int(t[0])
                stop = int(t[1])
                segments.append((start, stop))
    return segments



def play_segment(i, song, segments, speed):
    start = int(segments[i][0])
    stop = int(segments[i][1])
    utterance = song[start: stop]
    play_with_ffplay(utterance, speed)



def get_audiofile_info(filename):
    r = subprocess.check_output(['ffprobe', '-hide_banner', '-v', 'panic', '-show_streams', '-of', 'json', filename])
    r = json.loads(r)
    return r['streams'][0]



def get_audiofile_length(filename):
    """
        Get audio file length in seconds
    """
    return float(get_audiofile_info(filename)['duration'])


    
def play_with_ffplay(seg, speed=1.0):
    with NamedTemporaryFile("w+b", suffix=".wav") as f:
        seg.export(f.name, "wav")
        player = get_player_name()
        subprocess.call(
            [player, "-nodisp", "-autoexit", "-loglevel", "quiet", "-af", f"atempo={speed}", f.name]
        )



def convert_to_wav(src, dst, verbose=True):
    """
        Convert 16kHz wav
        Validate filename
    """
    if verbose:
        print(f"converting {src} to {dst}...")
    rep, filename = os.path.split(dst)
    dst = os.path.join(rep, filename)
    subprocess.call(['ffmpeg', '-v', 'panic',
                     '-i', src, '-acodec', 'pcm_s16le',
                     '-ac', '1', '-ar', '16000', dst])



def concatenate_audiofiles(file_list, out_filename, remove=True):
    if len(file_list) <= 1:
        return
    
    file_list_filename = "audiofiles.txt"
    with open(file_list_filename, 'w') as f:
        f.write('\n'.join([f"file '{wav}'" for wav in file_list]))
    
    subprocess.call(['ffmpeg', '-v', 'panic',
                     '-f', 'concat',
                     '-safe', '0',
                     '-i', file_list_filename,
                     '-c', 'copy', out_filename])
    os.remove(file_list_filename)
    
    if remove:
        for fname in file_list:
            os.remove(fname)



def list_files_with_extension(ext, rep, recursive=True):
    file_list = []
    if os.path.isdir(rep):
        for filename in os.listdir(rep):
            filename = os.path.join(rep, filename)
            if os.path.isdir(filename) and recursive:
                file_list.extend(list_files_with_extension(ext, filename))
            elif os.path.splitext(filename)[1] == ext:
                file_list.append(filename)
    return file_list
