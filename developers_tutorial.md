# Tutorial for integrating `nf-core` with PEP 
This tutorial aims to provide the necessary background for the developers that 
wish to incorporate PEP format into other `nf-core` 
[pipelines](https://nf-co.re/pipelines). The example implementation could be found 
in `taxprofiler` [pipeline](https://nf-co.re/taxprofiler).
An example of all changes needed to integrate PEP-`nf-core` can be found in 
[pull request](https://github.com/nf-core/taxprofiler/pull/133)
in `taxprofiler` repository.
The steps to accomplish PEP-`nf-core` integration for any `nf-core` pipeline are as follows:

1. Rewrite all pipeline input checks to [PEP schema](http://eido.databio.org/en/latest/writing-a-schema/).
2. If the script to check input does something more than input validation, then decouple the logic.
3. Add `--pep` input parameter for the pipeline.
4. Adjust the `nextflow_schema.json` to accept `--pep` parameter.
5. Install `eido/validate` and `eido/convert` modules from `nf-core` [modules](https://nf-co.re/docs/contributing/modules).
6. Adjust the workflow responsible for input check.
7. Create `test_pep` config so that users can run simple PEP input example.

Below one will find more detailed explanation of the tasks specified above as well 
as the "Other information" section, that will provide additional resources that may be 
useful during implementation.

## Steps to complete the integration
### 1. Rewrite all pipeline input checks
In general `nf-core` pipelines usually consist of `check_samplesheet.py` 
(or similarly named) Python script that is responsible for validation of 
`samplesheet.csv` file (eg. if all mandatory columns are present in the file, 
if all required columns have data, if extensions of the files are correct, etc.).
The goal of this task is to create a PEP schema from scratch, so that it exactly reflects
all the check from `check_samplesheet.py` Python script. 
[Example PEP schema](https://github.com/nf-core/taxprofiler/pull/133/files#diff-abc09af6a9de56ba2e40d0fa32a4c0f8c2cd30a0299488c4d922453ad20f3100) 
for `taxprofiler` pipeline is available in the pipeline code.

### 2. Decouple in case of emergency
In some cases previously mentioned `check_samplesheet.py` script not only was supposed to validate 
the input files, but was also adding additional column with information what type of reads
given row has.

Since `eido` is a tool just for validation, one can't add any column by using `eido/validate`. 
The best option here is to identify (within `check_samplesheet.py`) the logic responsible for modification
of the input file and move it to separate Python script (`bin/place_the_script_here.py` in `taxprofiler` source code). That way one can 
still  remove all the logic responsible for validation and replace it with `eido`, and modify the input
`samplesheet.csv` using newly extracted Python script.

### 3. Update --input parameter
It will be good if all the pipelines will share a common interface, so that users can run PEP with all the
pipelines the same way. Developer should adjust `--input` parameter to be able to accept also PEP config.

The developer must also update `nextflow_schema.json`. When adding new parameter to the pipeline,
he must adjust the `nextflow_schema.json` to avoid validation errors. The only thing needed here is to
allow passing `yaml` files in the schema.

### 4. Install `eido` modules
Eido is currently added as a module to `nf-core` modules. That way it can be shared across all the pipelines.
To be able to use `EIDO_VALIDATE` and `EIDO_CONVERT` commands in the pipeline, the developer first must install the
modules for current pipeline. There is available tutorial [how to install modules in a pipeline](https://nf-co.re/tools/#install-modules-in-a-pipeline).

### 5. Adjust the workflow responsible for input check
When incorporating new modules, the workflow will change. In my case changes were needed in 
`modules/local/samplesheet_check.nf` and `subworkflows/local/input_check.nf`.

### 6. Create test config
Developer should create test config so that user can run pipeline with PEP as input with minimal effort.
In order to do it, new config profile should be added as shown in `taxprofiler` [pull request containing
all changes](https://github.com/nf-core/taxprofiler/pull/133/files#diff-13b96be1e48daf716d5ac39dae9f905df6a0e0d4af0232e3f5c36fd52a178862).
Config will contain the minimal setup allowing to run analysis using PEP files.

## Other information
### How to add the tool to biocontainers
In general all necessary modules (`eido/validate` and `eido/convert`) are already added to `nf-core modules`,
but it may happen that the developer will need to add other tools. In order to do it, it's good to know how 
this works for `nf-core`. To be able to use any container in `nf-core` pipelines they should be hosted on 
`biocontainers` registry. Let's say that we want to add `peppy` as a tool and use it within a pipeline. 
There are two ways to accomplish that:

1. Put `peppy` to `bioconda`. This is the easiest way, and when `peppy` is available in `bioconda`, then
   `biocontainers` provide an automated container creation for this tool.
2. Manually add `peppy` to biocontainers. There is detailed 
   [tutorial how to add the tool to biocontainers](https://biocontainers-edu.readthedocs.io/en/latest/contributing.html) available.
