"""Preprocess raw audio into the specified format.

This script will convert every .mp3 & .flac files into .wav and also resample to 16kHz.

Please note that this script will utilize 80% of available thread
"""
import os
import argparse
from multiprocessing import Pool, cpu_count
import librosa
import soundfile as sf
from tqdm import tqdm
import sys

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")


def process(package):
    fpath, dst_sr, dst_path = package

    waveform, _ = librosa.load(path=fpath, sr=dst_sr)

    dst_fol = os.path.split(dst_path)[0]
    
    os.makedirs(dst_fol, exist_ok=True)
    sf.write(dst_path, waveform, dst_sr)

if __name__ == '__main__':

    # Create the parser
    parser = argparse.ArgumentParser()
    # Add an argument
    parser.add_argument('--ds_root', type=str, required=True, 
                        help="Root of dataset to be processed")
    parser.add_argument('--dst_root', type=str, required=True,
                        help="Destination root. Create a new directory if it doesn't exist")
    args = parser.parse_args()

    assert os.path.exists(args.ds_root), "ds_root does not exist"

    os.makedirs(args.dst_root, exist_ok=True)

    # Generate file's path
    file_paths = []
    for root, _, files in os.walk(args.ds_root):
        for f in files:
            if f.endswith('.flac') | f.endswith('.mp3'):
                fpath = os.path.join(root, f)
                file_paths.append(fpath)

    packages = []
    dst_sr = 16000
    for fpath in file_paths:
        sub_fol = fpath.replace(args.ds_root, "").strip("/").replace(".flac", ".wav").replace(".mp3", ".wav")
        dst_path = os.path.join(args.dst_root, sub_fol)
        if not os.path.exists(dst_path):
        
            p = (fpath, dst_sr, dst_path)
            packages.append(p)

    print("There're {} file".format(len(packages)))
    n_threads = int(cpu_count() * 0.8)
    with Pool(n_threads) as p:
        with tqdm(total=len(packages)) as pbar:
            for _ in p.imap(process, packages):
                pbar.update()