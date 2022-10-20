import logging
logging.disable(logging.CRITICAL)  # We dont want blah blah
from prettytable import PrettyTable
from os.path import exists
import os
import argparse
import datetime
import nemo.collections.asr as nemo_asr

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', type=str, required=True,
                         help="Model file to use")
    parser.add_argument('files', nargs='+',
                        help='Path to a file(s).')
    args = parser.parse_args()

    if not exists(args.model):
        raise Exception(f'Model file {args.model} not found')

    print(f'loading {args.model}...')
    model = nemo_asr.models.ctc_models.EncDecCTCModel.restore_from(restore_path=args.model)
    print('model loaded')

    for file in args.files:
        if not exists(file):
            print(f'{file} does not exist, skipped it')
            args.files.remove(file)

    from pyctcdecode import build_ctcdecoder
    print ('loading decoder')
    decoder = build_ctcdecoder(model.decoder.vocabulary)
    start = datetime.datetime.now()
    logits = model.transcribe(paths2audio_files=args.files, batch_size=max(
        os.cpu_count(), 1), logprobs=True)
    
    table = PrettyTable()
    import multiprocessing

    with multiprocessing.get_context("fork").Pool() as pool:
        preds = decoder.decode_batch(pool, logits)
    
    table.add_column("File", args.files)
    table.add_column("Text", preds)
    print (table)

    end = datetime.datetime.now()
    delta = end - start
    print(f'Took {delta.total_seconds()} seconds.')


if __name__ == '__main__':
    main()
