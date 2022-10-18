#!/usr/bin/python
# -*- coding: utf-8 -*-

from omegaconf import DictConfig
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.loggers import WandbLogger
import pytorch_lightning as pl
import nemo.collections.asr as nemo_asr
from ruamel.yaml import YAML

def main():
    # Read params
    config_path = 'quartznet_15x5.yaml'
    yaml = YAML(typ='safe')
    with open(config_path) as f:
        params = yaml.load(f)

    # initialize W&B logger and specify project name to store results to
    project = params['exp_manager']['wandb_logger_kwargs']['project']
    run_id = params['exp_manager']['wandb_logger_kwargs']['name']
    wandb_logger = WandbLogger(project=project, name=run_id, log_model='all')
    # set config params for W&B experiment
    for (k, v) in params.items():
        wandb_logger.experiment.config[k] = v

    # Extract new target vocab, the base model was trained for English, we need to change target vocab to this one as we are finetuning for a new language
    vocab = params['model']['labels']

    # Initialize our model from English model pretrained by Nvidia
    quartznet_model = nemo_asr.models.EncDecCTCModel.from_pretrained(
        model_name=params['init_from_pretrained_model'])
    # Replace vocabulary with the new one
    quartznet_model.change_vocabulary(new_vocabulary=vocab)

    # Setup train and test datasets
    quartznet_model.setup_training_data(train_data_config=params['model'
                                                                 ]['train_ds'])
    quartznet_model.setup_validation_data(val_data_config=params['model'
                                                                 ]['validation_ds'])

    quartznet_model.setup_optimization(optim_config=DictConfig(params['model'
                                                                      ]['optim']))

    # We only log checkpoints when model performs better on WER
    checkpoint_callback = ModelCheckpoint(monitor='val_wer', mode='min')
    trainer = pl.Trainer(
        accelerator='gpu',
        devices=1,
        max_epochs=500,
        logger=wandb_logger,
        amp_level='O1',
        amp_backend='apex',
        precision=16,
        callbacks=[checkpoint_callback],
    )
    quartznet_model.set_trainer(trainer)

    # Train!
    trainer.fit(quartznet_model)

    # Save final model as a NeMo file.
    quartznet_model.save_to('finetuned.nemo')


if __name__ == '__main__':
    main()  # noqa pylint: disable=no-value-for-parameter
