# Devisa: STT-models for different Romansh dialects

In this folder you can find our submission for the competition. The source-code repository is available as a submodule here.
A copy is also provided separately just in case this is not sufficient.

All of the models that were created for the project are available on the [project's Gitlab package repository](https://gitlab.com/prvInSpace/romansh-stt-project/-/packages)
in a tflite format. The KenLM language models created for each of the dialects are also available there and the custom splits of the Common Voice datasets.

## Important links:
* The main repository for the source code can be found at [Gitlab](https://gitlab.com/prvInSpace/romansh-stt-project).
* The video submission can be found at [Google Drive](https://drive.google.com/file/d/17Tfj7nfZEhVOid7HqhnqZGwM_V9zLT4w/view?usp=sharing)
* The spreadsheet used to record the results can be found at [Google Spreadsheets](https://docs.google.com/spreadsheets/d/1TBw0GrosfgvsdqPXYzgkaN3ZsMQys8574L6bhlNh4rw/edit?usp=sharing)
* The main README file for the project can be found in the source-code folder.

## How to recreate the results

The source-code folder doesn't contain any of the Common Voice data, and to run anything you need to setup the environment. the Makefile should be able to recreate the environment, simply by running `make`. This should download the Common Voice datasets, and perform all of the required preprocessing (This was tested on a Linux system and seemed to work)

After that if you want to copy in the models and language-models instead of retraining them, please unzip the `models.zip` and the `lm-models.zip` files and move/copy the folders to the source-code folder. Alternatively you can find tflite versions on the [project's Gitlab package repository](https://gitlab.com/prvInSpace/romansh-stt-project/-/packages)

Note that the application that splits the Common Voice dataset is non-deterministic.
As such, if you want to recreate the results, you can find the custom splits both in the `splits/` folder in the source-code directory and in the individual packages for RM-Sursilv and RM-Vallader on the [project's Gitlab package repository](https://gitlab.com/prvInSpace/romansh-stt-project/-/packages). For your convenience these will be copied into the correct folder when you run the `make` command.

The Docker environment can be started via the Makefile using a couple of flags. The most notable of which is LANG which specifies which language-code to target.
For example, to create an environment with both spoken and text data for rm-sursilv, this can be done by calling:
```bash
make train LANG=rm-sursilv
```

Once in the environment you can rerun the tests by either running:
```bash
bash /scripts/eval.bash
```
if you want to test it without the language model or by running:
```bash
bash /scripts/eval_scorer.bash
```
if you want to test it with the language model.

You can specify which language model you want by adding the LM flag when starting the Docker and you can also specify which Common Voice dataset you want by using the DATA flag as such:
```bash 
make train LANG=rm-sursilv DATA=rm-vallader LM-rm-puter 
```

That should be everything.
If you just want to test the best performance for RM-Sursilv and RM-Vallader, then LANG should be the only required flag.
