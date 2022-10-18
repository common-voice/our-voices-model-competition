# Devisa: STT-models for different Romansh dialects

In this folder you can find our submission for the competition. The source-code repository is available as a submodule here.
A copy is also provided separately just in case this is not sufficient.

All of the models that were created for the project are available on the [project's Gitlab package repository](https://gitlab.com/prvInSpace/romansh-stt-project/-/packages)
in a tflite format. The KenLM language models created for each of the dialects are also available there and the custom splits of the Common Voice datasets.

## How to recreate the results

The Makefile should be able to recreate the environment, simply by running `make`.

Note that the application that splits the Common Voice dataset is non-deterministic.
As such, if you want to recreate the results, you can find the custom splits both in the `splits/` folder in the source-code directory and in the individual packages for RM-Surilv and RM-Vallader on the [project's Gitlab package repository](https://gitlab.com/prvInSpace/romansh-stt-project/-/packages).

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
make train LANG=rm-sursilv DATA=rm-vallader LM-rm-putin 
```

That should be everything.
If you just want to test the best performance for RM-Sursilv and RM-Vallader, then LANG should be the only required flag.
