# Common Voice Toolbox

A rather large-scale(-to-be) system and workflow for Common Voice related work.

This toolbox aims to help all language communities, scientists and experts who deal with Common Voice or use it. The main idea behind it is: "To fight bias, you need to know your dataset and try to correct the problems for the next version". The suggested system and workflow takes dataset health and quality at the center and tries to provide tools for pinpointing and correcting any kind of bias.

In the timeframe given in Our Voices, only a portion of the CV-Toolbox could be fully implemented, so I open-source them with this application.

## Why and How

When I first approached to Our Voices, I saw that we don’t have the tools necessary to achieve the goals easily for Common Voice datasets for many reasons. Instead of creating a custom solution or working on a single model, I decided to suggest a new workflow and build the open-sourced Common Voice Toolbox, so that everybody on CV can benefit in the future. I've been dealing with Common Voice Turkish for more than a year now and recently started to also work on other Turkic languages, and problems multiplied.

I’m trying to solve the following problems, not a full list, but covers the main topics:

- Common Voice is a crowd-sourced project. It is like an experiment running in a semi-controlled environment. Thus, the experiment results as they are will not be fully reliable and/or be chaotic (e.g. in terms of gender distribution in a dataset).
- Not all community leads in Common Voice are programmers or AI experts. Or even if they are they would need to spare some time to work on datasets. And even they do find the time, most of the work becomes duplicated, spending many resources of this planet unnecessarily. This is particularly true for low-resourced languages where people working on them are few.
- Existing workflows only include a single dataset, there is no support for multiple versions or languages and if you build loops they become inefficient. For example, in consequitive versions of a dataset, you keep converting the same mp3 files and measure the duration. Or you have to write custom code to deal with it.
- Many statistical data is not available for CV language communities in human readable format to assess their dataset status or some data can only be reached during training workflow. These include all the data in the metadata, text-corpus and individual splits. To get some idea on the dataset versions for Turkish I used to use Excel, but after the release schedule dropped to 3 months periods, it became rather tedious. I needed to automate this, and asked myself: "why not do it for everybody?"...
- As a community lead, I need to know how we are doing. How is the voice bias, how is demographics distribution, how is the text-corpus related to voice-corpus? Was the text-corpus enough, are these sentences recorded with too many voices? What portion of sentences are too long? Etc, etc. To create an unbiased model, you first need a more-or-less balanced dataset, and this is a long process between versions.
- The default splits in CV are not enough for usable and diverse enough models, not even usable as a baseline. These were especially valid for low-resourced languages. There was a need to create custom splits and have abilitity to measure the diversity in them - before even trying to create unbiased models.
- The demographics data in CV datasets are not healty, not realiable to be used as it is (this has many reasons but this is not the place for these). It needs moderation before being used to create unbiased models (ref. Artie Bias Corpus). But such corpora are only valid for a time and should be updated with the dataset size increase. We need moderation/annotation tools which can be used across versions. Moderation tools to check the validity of reported sentences, down-voted ones, annotating the demographic info, checking the clean/noisy recording quality, etc. This may be a tool to run on local, or better should be accessable from Internet, prefably in a server-less scenario.
- In slico tests we do during training are not enough. We need to measure the actual performance in the wild, using the test set of the model, using real voices in real-world environments and measuring CER/WER and sentence similarity and reporting them. Again preferably in a serverless scenario.
- The most scarse resource for many languages are CC-0 sentences and without them the datasets get transcript biases. Adding large scale resources like Wikipedia are also not easy and even can result in a worse dataset. The best resource for text-corpus is ourselves. We need a custom solution for moderated, domain focused CC-0 chat application.
- ...

So, we need tooling specific for Common Voice, to fix possible problems and fill-in the missing parts, for the democratization of Voice and to be able to create unbiased models in the future.

## Suggested Toolbox and Workflow

This tentative diagram shows the tools in the suggested toolbox and workflow.

[DIAGRAM]

## Project Status

Below you can find short descriptions of the boxes in the above diagram with their status and links to their repositories.

### Released (and WIP, as some need to be beta tested after release)

The following repositories are released with this Our Voices application as beta versions. To get detailed information, please follow the links on the headers to individual repositories where detailed information resides.

#### [cv-tbox - Diversity Check](https://github.com/HarikalarKutusu/common-voice-diversity-check)

Scripts for creating alternative scripts and collecting simple statistical information for multiple languages, versions and splitting algorithms. In addition to tsv output, it also provides an Excel file to examine the results side-by-side. One of these algorithms had been suggested for Common Voice use (nicknamed v1). This repo will eventually be part of the core.

#### [cv-tbox - Dataset Compiler](https://github.com/HarikalarKutusu/cv-tbox-dataset-compiler)

A collection of scripts to join voice-corpora, text-corpora and clip duration tables from different local resources and get statistics from them, so it is a data and statistics "compiler". It outputs tsv and json files for further use. JSON output is used directly in [Common Voice Dataset Analyzer](https://github.com/HarikalarKutusu/cv-tbox-dataset-analyzer). As of this PR, I analyzed all languages on CV (100 as of v11.0), all datasets between v8.0-v11.0 (+added some more from the datasets we had on file from past - total 392 datasets), using 3 splitting algorithms, totaling analysis of 1163 split combinations and nearly 3900 tsv files. We will continue to go back in time for completeness and of course update the data in new CV versions. This repo will eventually be part of the core.

#### [cv-tbox - Metadata Viewer](https://github.com/HarikalarKutusu/cv-tbox-metadata-viewer)

A serverless WebApp to visualize all datasets in CV metadata from commonvoice-dataset repo. You can see the total Common Voice sums, compare languages and/or a single language across versions, with tables and graphs. It fully depends on the data provided by CV and cannot provide detailed analysis.

![cv-tbox-metadata-viewer-1](https://user-images.githubusercontent.com/8849617/196776948-ca88dc68-0f85-4dc1-880b-cfe3aea00ffd.png)

#### [cv-tbox - Dataset Analyzer](https://github.com/HarikalarKutusu/cv-tbox-dataset-analyzer)

A serverless WebApp to visualize the results of cv-tbox-dataset-compiler, detailed information on splits, algorithms, durations and text-corpus. Currently you can only get detailed information on a single dataset but compare the splitting algorithms with tables and graphs. More detailed measures and graphs will follow shortly.

![cv-tbox-dataset-analyzer-2](https://user-images.githubusercontent.com/8849617/196783472-c6267eaf-40e5-4cc6-b505-37c925775330.png)

### WIP and not yet released publicly

- **cv-tbox-core**: Python and experiment based tool to split/join/check/import/export/convert/correct/moderate/sample/split/etc... multiple datasets from multiple languages and versions, running locally. This is where most of the python tools will join (needs a second rework due to increasing parameters). It is currently used to download and export the CV metadata for cv-tbox-metadata-viewer.
- **cv-tbox-moderator**: A project based WebApp (node/react) to moderate/annotate datasets. The datasets/recordings will not be uploaded to the server, only moderation results will be kept.
- **cv-tbox-real-world-testers**: A project based WebApp (node/react) to test different models with different backbones. The datasets/recordings will not be uploaded to the server, only test results will be kept. Our initial work uses Coqui STT with new stt-wasm, which provides a serverless solution. Coqui STT client-server and Nvidia implementations will follow.

### Not started

- **cv-tbox-cc0-corpora-chat**: A multi-domain, multi-language, multi-project moderated CC-0 chat application. It will use rules from CV codes and make people chat in rooms. Results will be exported to be imported to the Sentence Collector.
- **cv-tbox-documentation**: The full documentation repo to be released on readthedocs (partly started but postponed due to Our Voices).
- **cv-tbox-data**: Links to downloadable data for test and production use.
- **cv-tbox-examples**: Examples mainly for cv-tbox-core uses.
- **common-voice-toolbox-package**: A package containing all of the above.

Notes:

- This is an ongoing process, I make multiple commits per day to enhance the packages.
- We do not collect any kind of analytics info. In case of server based tools we will publish, the users will be able to delete all the data when they are done.

## Other

### Code and Data

Codes are in their related repositories. The first two do not include the data. The final/compiled data is publicly in the WebApps.

In case you insist on running the code again, I uploaded the data [here](https://drive.google.com/drive/folders/1ehE7c3jzxGt797RVJov2jGitw2CB-uVi?usp=sharing). You should put them under experiment or data directories. Beware, the data is 7.1 GB's 7zipped...

Feature requests and issues are very much welcome.

### About the "v1" Splitting Algorithm

As I presented the algorithm to Common Voice in a separate process, I do not include it into Our Voices. But I did include the splitting data into the Dataset Analyzer and explained it in the repo. I also trained a couple of datasets and compared them, showing promising results. It results in better voice and demographic distribution and much better training results compared to the existing CorporaCreator.

### License

AGPL 3.0
