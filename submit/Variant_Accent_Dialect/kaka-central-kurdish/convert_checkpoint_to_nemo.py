import logging
logging.disable(logging.CRITICAL)
import nemo.collections.asr as nemo_asr
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('checkpoint')
    parser.add_argument('output')
    args = parser.parse_args()

    print ('loading...')
    model = nemo_asr.models.ctc_models.EncDecCTCModel.load_from_checkpoint(args.checkpoint, strict=False)
    print ('loaded, converting now...')
    model.save_to(args.output)
    print ('done.')

if __name__ == '__main__':
    main()