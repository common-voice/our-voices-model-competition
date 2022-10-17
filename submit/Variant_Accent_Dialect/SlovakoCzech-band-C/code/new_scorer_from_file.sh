#!/bin/bash
#handy script to create a scorer (in /data/scorers/FILENAME.scorer) out of Your txt file 
#make sure that /data/scorers and /data/lms directories exist
#run as bash new_scorer_from_file.sh FILENAME
source /data/deepspeech-train-jetson-venv/bin/activate
mkdir /data/lms/$1
python3 /data/DeepSpeech/data/lm/generate_lm.py --input_txt $1 --output_dir /data/lms/$1 --top_k 1000000 --kenlm_bins /data/utils/kenlm/build/bin/ --arpa_order 4 --max_arpa_memory "1%" --arpa_prune "0|0|1" --binary_a_bits 255 --binary_q_bits 8 --binary_type trie --discount_fallback
/data/utils/generate_scorer_package --lm /data/lms/$1/lm.binary --vocab /data/lms/$1/vocab-1000000.txt  --checkpoint /data/alphabets/deepspeech/csk --package /data/scorers/$1.scorer --default_alpha 1 --default_beta 4
