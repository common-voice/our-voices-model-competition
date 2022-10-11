#!/usr/bin/env bash


echo "running path.sh"
. ./path.sh
echo "running cmd.sh"
. ./cmd.sh

nj=3       # number of parallel jobs - 1 is perfect for such a small dataset
lm_order=3 # language model order (n-gram quantity) - 1 is enough for digits grammar
stage=$1

# Safety mechanism (possible running this script with modified arguments)
. utils/parse_options.sh || exit 1


[[ $# -eq 0 ]] && { echo "Wrong arguments!"; exit 1; }

if [ $stage -eq -1 ]; then
    echo
    echo "===== PREPARING DATA ====="
    echo
    
    # Removing previously created data (from last run.sh execution)
    rm -rf exp mfcc data
    
    
    # Needs to be prepared by hand (or using self written scripts):
    #
    # spk2gender  [<speaker-id> <gender>]
    # wav.scp     [<uterranceID> <full_path_to_audio_file>]
    # text        [<uterranceID> <text_transcription>]
    # utt2spk     [<uterranceID> <speakerID>]
    # corpus.txt  [<text_transcription>]
   
    #python3 build_kaldi_files.py corpus/train || exit 1
    #python3 build_kaldi_files.py corpus/test || exit 1
fi

if [ $stage -ge 0 ]; then
    echo
    echo "===== VALIDATING DATA ====="
    echo
    
    # Making spk2utt files
    utils/utt2spk_to_spk2utt.pl data/train/utt2spk > data/train/spk2utt
    utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt
    
    echo
    utils/validate_data_dir.sh --no-feats data/train
    utils/validate_data_dir.sh --no-feats data/test
    
    utils/fix_data_dir.sh data/train          # tool for data proper sorting if needed - here: for data/train directory
    utils/fix_data_dir.sh data/test
    
    utils/prepare_lang.sh data/local/dict_nosp "<UNK>" data/local/lang_tmp_nosp data/lang_nosp
    utils/validate_lang.pl data/lang_nosp
    utils/validate_dict_dir.pl data/local/dict_nosp
    echo "done"
fi

if [ $stage -ge 1 ]; then
    echo
    echo "===== FEATURES EXTRACTION ====="
    echo
    # Making feats.scp files
    mfccdir=mfcc
    
    steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/train exp/make_mfcc/train $mfccdir
    steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/test exp/make_mfcc/test $mfccdir
    
    # Making cmvn.scp files
    steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train $mfccdir
    steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test $mfccdir
fi


if [ $stage -ge 2 ]; then
    echo
    echo "===== LANGUAGE MODEL CREATION ====="
    echo "==== MAKING lm.arpa ===="
    echo
    loc=`which ngram-count`;
    if [ -z $loc ]; then
            if uname -a | grep 64 >/dev/null; then
                sdir=$KALDI_ROOT/tools/srilm/bin/i686-m64
            else
                sdir=$KALDI_ROOT/tools/srilm/bin/i686
            fi
            if [ -f $sdir/ngram-count ]; then
                echo "Using SRILM language modelling tool from $sdir"
                export PATH=$PATH:$sdir
            else
                echo "SRILM toolkit is probably not installed.
                      Instructions: tools/install_srilm.sh"
                exit 1
            fi
    fi
    local=data/local
    mkdir $local/tmp
    ngram-count -order $lm_order -write-vocab $local/tmp/vocab-full.txt -wbdiscount -text $local/corpus.txt -lm $local/tmp/lm.arpa
    
    mkdir $local/lm
    gzip -c $local/tmp/lm.arpa > data/local/lm/lm_tglarge.arpa.gz
    
    echo "done"
fi


if [ $stage -ge 3 ]; then
    echo
    echo "==== MAKING G.fst ===="
    echo
    local=data/local
    lang=data/lang_nosp
    arpa2fst --max-arpa-warnings=-1 --disambig-symbol=#0 \
             --read-symbol-table=$lang/words.txt \
             $local/tmp/lm.arpa \
             $lang/G.fst
    tar -czvf $local/tmp/lm.arpa.gz $local/tmp/lm.arpa
    
    # Create ConstArpaLm format language model for full 3-gram and 4-gram LMs
    utils/build_const_arpa_lm.sh $local/lm/lm_tglarge.arpa.gz \
                                 $lang data/lang_nosp_test_tglarge
fi

if [ $stage -ge 4 ]; then
    echo
    echo "===== MONO TRAINING ====="
    echo
    steps/train_mono.sh --boost-silence 1.25 --nj $nj --cmd "$train_cmd" \
                        data/train data/lang_nosp exp/mono  || exit 1

    echo
    echo "===== MONO DECODING ====="
    echo
    utils/mkgraph.sh --mono data/lang_nosp exp/mono exp/mono/graph || exit 1
    #steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/mono/graph data/test exp/mono/decode
    echo
    echo "===== MONO ALIGNMENT ====="
    echo
    steps/align_si.sh --boost-silence 1.25 --nj $nj --cmd "$train_cmd" data/train data/lang_nosp exp/mono exp/mono_ali_train || exit 1
fi

if [ $stage -ge 5 ]; then
    echo
    echo "===== TRI1 (first triphone pass) TRAINING ====="
    echo
    # train a first delta + delta-delta triphone system on all utterances
    # Set to 2000 HMM states an 11000 Gaussians
    steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" 2000 10000 data/train data/lang_nosp exp/mono_ali_train exp/tri1 || exit 1
    echo
    echo "===== TRI1 (first triphone pass) DECODING ====="
    echo
    utils/mkgraph.sh data/lang_nosp exp/tri1 exp/tri1/graph || exit 1
    #steps/decode.sh --config conf/decode.config --nj $nj --cmd "$decode_cmd" exp/tri1/graph data/test exp/tri1/decode
    echo
    echo "===== TRI1 ALIGNMENT ====="
    echo
    steps/align_si.sh --nj $nj --cmd "$train_cmd" data/train data/lang_nosp exp/tri1 exp/tri1_ali_train
fi

if [ $stage -ge 6 ]; then
    echo
    echo "===== train an LDA+MLLT system ====="
    echo
    steps/train_lda_mllt.sh --cmd "$train_cmd" --splice-opts "--left-context=3 --right-context=3" 2500 15000 data/train data/lang_nosp exp/tri1_ali_train exp/tri2b
    echo
    echo "===== Align utts using the tri2b model ====="
    echo
    steps/align_si.sh --nj $nj --cmd "$train_cmd" --use-graphs true data/train data/lang_nosp exp/tri2b exp/tri2b_ali_train
fi

if [ $stage -ge 7 ]; then
    echo
    echo "===== Train tri3b, which is LDA+MLLT+SAT ====="
    echo
    steps/train_sat.sh --cmd "$train_cmd" 2500 15000 data/train data/lang_nosp exp/tri2b_ali_train exp/tri3b
fi

# Now we compute the pronunciation and silence probabilities from training data,
# and re-create the lang directory.
if [ $stage -ge 8 ]; then
    echo
    echo "===== compute the pronunciation and silence probabilities ====="
    echo
    steps/get_prons.sh --cmd "$train_cmd" \
        data/train data/lang_nosp exp/tri3b
  
    utils/dict_dir_add_pronprobs.sh --max-normalize true \
        data/local/dict_nosp \
        exp/tri3b/pron_counts_nowb.txt exp/tri3b/sil_counts_nowb.txt \
        exp/tri3b/pron_bigram_counts_nowb.txt data/local/dict
  
    utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang_tmp data/lang
    utils/validate_lang.pl data/lang
    utils/validate_dict_dir.pl data/local/dict
  
  echo "******* format_lms **********"
  #local/format_lms.sh --src-dir data/lang data/local/lm
  for lm_suffix in tgsmall tgmed; do
      # tglarge is prepared by a separate command, called from run.sh; we don't
      # want to compile G.fst for tglarge, as it takes a while.
      test=data/lang_test_${lm_suffix}
      mkdir -p $test
      cp -r data/lang/* $test
      arpa2fst --disambig-symbol=#0 \
               --read-symbol-table=$test/words.txt \
               data/local/tmp/lm.arpa $test/G.fst
      utils/validate_lang.pl --skip-determinization-check $test || exit 1;
  done
  
  echo "******* build_const_arpa *****"
  utils/build_const_arpa_lm.sh data/local/lm/lm_tglarge.arpa.gz \
                                 data/lang data/lang_test_tglarge
  
  echo "****** align_fmllr ********"
  steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" \
    data/train data/lang exp/tri3b exp/tri3b_ali_train
fi


if [ $stage -ge 9 ]; then
    echo
    echo "===== STAGE 9 ====="
    echo "==== Test the tri3b system with the silprobs and pron-probs ===="
    echo
    
    # decode using the tri3b model
    utils/mkgraph.sh data/lang_test_tgsmall \
                     exp/tri3b exp/tri3b/graph_tgsmall
    
    echo "****** decode_fmllr.sh ******"
    steps/decode_fmllr.sh --nj $nj --cmd "$decode_cmd" \
                          exp/tri3b/graph_tgsmall data/test \
                          exp/tri3b/decode_tgsmall_test
    
    echo "****** lmrescore.sh ******"
    steps/lmrescore.sh --cmd "$decode_cmd" data/lang_test_{tgsmall,tgmed} \
                       data/test exp/tri3b/decode_{tgsmall,tgmed}_test
    
    echo "****** lmrescore_const_arpa.sh ******"
    steps/lmrescore_const_arpa.sh \
        --cmd "$decode_cmd" data/lang_test_{tgsmall,tglarge} \
        data/test exp/tri3b/decode_{tgsmall,tglarge}_test
fi


if [ $stage -ge 10 ]; then
    echo
    echo "===== STAGE 10 ====="
    echo "==== Train a chain model ===="
    echo
    
    #local/chain2/run_tdnn_nogpu.sh
    local/chain/run_tdnn_1j_nogpu.sh    # VOSK compatible recipe
    #local/chain/run_tdnn_1j_nogpu_skinny.sh
    #local/chain/run_tdnn_1j_nogpu_short.sh
    #local/chain/run_tdnn_1j_nogpu_short-skinny.sh
    #local/chain/run_tdnn_1j_nogpu_shorter.sh
    #local/chain/run_tdnn_1j_nogpu_shorter-skinny.sh
fi

echo
echo "===== run.sh script is finished ====="
echo
