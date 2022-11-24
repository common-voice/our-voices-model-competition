#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import fastwer
import sys



if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:", sys.argv[0], "ground_truth.txt hyp.txt")
    
    gt_file = sys.argv[1]
    hyp_file = sys.argv[2]
    
    gt_corpus = []
    hyp_corpus = []
    
    with open(gt_file, 'r') as f:
        gt_corpus = " ".join([line.strip().lower() for line in f.readlines()])
        #gt_corpus = [line.strip().lower() for line in f.readlines()]
    with open(hyp_file, 'r') as f:
        hyp_corpus = " ".join([line.strip().lower() for line in f.readlines()])
        #hyp_corpus = [line.strip().lower() for line in f.readlines()]

    
    print("WER {}%".format(round(fastwer.score_sent(hyp_corpus, gt_corpus), 1)))
    print("CER {}%".format(round(fastwer.score_sent(hyp_corpus, gt_corpus, char_level=True), 1)))
