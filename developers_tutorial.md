# Tutorial for integrating `nf-core` with PEP 

## Introduction and summary

This tutorial explains how to adapt `nf-core` 
[pipelines](https://nf-co.re/pipelines) to accept sample metadata in PEP format.
An example implementation can be found 
in the `taxprofiler` [pipeline](https://nf-co.re/taxprofiler). 
A pull request with all the changes needed can be found here. 
The steps to accomplish that are as follows:

1. Rewrite all pipeline input checks to [PEP schema](http://eido.databio.org/en/latest/writing-a-schema/).
2. If the script to check input does something more than input validation, then decouple the logic.
3. Add `--pep` input parameter for the pipeline.
4. Adjust the `nextflow_schema.json` to accept `--pep` parameter.
5. Install `eido/validate` and `eido/convert` modules from `nf-core` [modules](https://nf-co.re/docs/contributing/modules).
6. Adjust the workflow responsible for input check.
7. Create `test_pep` config so that users can run simple PEP input example.

Below is detailed explanation of these tasks as well 
as other information with additional resources that may be 
useful during implementation.

## 1. Rewrite all pipeline input checks

In general, `nf-core` pipelines usually consist of a `check_samplesheet.py` 
(or similarly named) Python script that is validates the 
`samplesheet.csv` file. This validation checks if all mandatory columns are present in the file, 
if all required columns have data, if extensions of the files are correct, etc.

Here, we propose switching this approach to insetad use a PEP schema, so that the PEP validator (`eido`) can be used to accomplish 
all checks formerly performed by `check_samplesheet.py`. Example PEP schema for `taxprofiler`
pipeline can be found here.

## 2. Decouple in case of emergency
In some cases previously mentioned `check_samplesheet.py` script not only was supposed to validate 
the input files, but was also adding additional column with information what type of reads
given row has.

Since `eido` is a tool just for validation, one can't add any column by using `eido/validate`. 
The best option here is to identify (within `check_samplesheet.py`) the logic responsible for modification 
of the input file and move it to separate Python script (`bin/place_the_script_here.py`). That way one can 
still  remove all the logic responsible for validation and replace it with `eido`, and modify the input
`samplesheet.csv` using newly extracted Python script.

## 3. Add PEP as input parameter
It will be good if all the pipelines will share a common interface, so that users can run PEP with all the
pipelines the same way. To accomplish that, the `--pep` parameter should be added to the pipeline.
Developer should allow pipeline to consume `--pep` parameter and make it mandatory to provide either `--input`
or `--pep` when running a pipeline (by default user must always pass `--input`). In case of `taxprofiler` pipeline
two files had to be edited: `lib/WorkflowMain.groovy` and `workflows/taxprofiler.nf`.

## 4. Adjust `nextflow_schema.json`
This step is strongly coupled with `3. Add PEP as input parameter`. When adding new parameter to the pipeline,
one must adjust the `nextflow_schema.json` to avoild validation errors. The only thing needed here is to tell
that instead of one mandatory argument (`--input`), we will now have one of `[--input, --pep]` as mandatory.

## 5. Install `eido` modules
Eido is currently added as a module to `nf-core` modules. That way it can be shared across all the pipelines.
To be able to use `EIDO_VALIDATE` and `EIDO_CONVERT` commands in the pipeline, the developer first must install the
modules for current pipeline. Tutorial how to do it can be found 
[here](https://nf-co.re/tools/#install-modules-in-a-pipeline).

## 6. Adjust the workflow responsible for input check
When incorporating new modules, the workflow will change. In my case changes were needed in 
`modules/local/samplesheet_check.nf` and `subworkflows/local/input_check.nf`.

## 7. Create test config
Developer should create test config so that user can run pipeline with PEP as input with minimal effort.
In order to do it, new config profile should be added as shown in `taxprofiler` pull request.

## 8. Other information
### Biocontainers
In general all necessary modules (`eido/validate` and `eido/convert`) are already added to `nf-core modules`,
but it may happen that the developer will need to add other tools. In order to do it, it's good to know how 
this works for `nf-core`. To be able to use any container in `nf-core` pipelines they should be hosted on 
`biocontainers` registry. Let's say that we want to add `peppy` as a tool and use it within a pipeline. 
There are two ways to accomplish that:

1. Put `peppy` to `bioconda`. This is the easiest way, and when `peppy` is available in `bioconda`, then
   `biocontainers` provide an automated container creation for this tool.
2. Manually add `peppy` to biocontainers. Detailed tutorial how to do it is available 
   [here](https://biocontainers-edu.readthedocs.io/en/latest/contributing.html).
