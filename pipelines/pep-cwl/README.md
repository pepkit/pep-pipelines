# pep-cwl

## Motivation

One common task in bioinformatics is to run a bunch of samples independently through a workflow. Often, samples are listed in a CSV sample table with one row per sample. We'd like to be able to easily run a CWL workflow on each row of the sample table.

One sample table CSV standard is [PEP](http://pep.databio.org), which specifies structure for sample metadata. This repository demonstrates how to run a PEP metadata table through a CWL pipeline.

The [simple demo](/simple_demo) runs `wc` on a few text files as input.  The [bioinformatics_demo](/bioinformatics_demo), which runs `bwa` alignment on some sequencing data.

## Simple demo

### CWL tool description

Here is a [CWL tool description](simple_demo/wc-tool.cwl) that runs `wc` to count lines in an input file. Invoke it on a [simple job](simple_demo/wc-tool.yml) like this:

```
cwl-runner wc-tool.cwl wc-job.yml
```

This runs the workflow for one input. How can we run it across multiple samples in a CSV file? CWL has built-in scatterers, but we want to simplify things to run across a CSV sample table.

### PEP-formatted sample metadata

Our sample data is stored in a [sample table](simple_demo/file_list.csv) with two rows, one per sample. Each row points to a corresponding input file in the [data](simple_demo/data) subdirectory. This sample table along with the [project config file](simple_demo/project_config.yaml) together make up a standard PEP (see [pep.databio.org](http://pep.databio.org) for formal spec).

We'd like to run our CWL workflow/tool on each of these samples, which means running it once per row in the sample table. We can accomplish this with [looper](http://looper.databio.org). From a CWL perspective, looper is a *tabular scatterer* -- it will scatter a CWL workflow across each row in a sample table independently.

### Using looper

Looper uses a [pipeline interface](simple_demo/cwl_interface.yaml) to describe how to run `cwl-runner`. In this interface we've simply specified a `command_template:`, which looks like the above CWL command: `cwl-runner wc-tool.yaml {sample.sample_yaml_cwl}`. The `{sample.sample_yaml_cwl}` is a variable that will be populated by looper to refer to a `yaml` file looper creates for each sample. This is a result of the `looper.write_sample_yaml_cwl` item listed in the `pre_submit` section of the pipeline interface.

To run these commands, invoke `looper run`, passing the project configuration file, like this:

```
looper run project_config.yaml
```

This will run the `cwl-runner wc-tool.cwl ...` command on *each row in the sample table*. While there is also a built-in CWL approach to scatter workflows, there are a few nice things about the looper approach:

- **PEP framework benefits**. PEPs are a third-party specification for describing sample metadata, complete with a [validation platform called eido](http://eido.databio.org). PEP provides powerful portability features like [derived attributes](http://pep.databio.org/en/latest/specification/#sample-modifier-derive), and [implied attributes](http://pep.databio.org/en/latest/specification/#sample-modifier-imply), which adjust sample attributes on-the-fly, and [project config imports](http://pep.databio.org/en/latest/specification/#project-modifier-import) and [project config amendments](http://pep.databio.org/en/latest/specification/#project-modifier-amend) to re-use project components and define sub-projects. Finally, because PEP is not tied to a specific pipeline framework, your sample annotations are reusable across other pipelines; for instance, Snakemake can also natively read a PEP-formatted project.
- looper provides a CLI with lots of other nice features for job management, outlined in the [looper docs](http://looper.databio.org/en/latest/features/).

## Bioinformatics demo

This demo will run a basic bowtie2 alignment.

Running example:

```
PATH="$PATH:$HOME/apps/bowtie2-2.4.1-linux-x86_64" looper run bioinformatics_demo/pep_bio.yaml
```



### Other looper features

#### Initialize the repository for easier CLI access

```
looper init project_config.yaml
```

Then run from this directory without passing the config file:

```
looper run
```


### Switch back-end computing infrastructure with divvy

Use [divvy](http://divvy.databio.org) to customize available computing once, then use it on all your workflows. 

```
looper run --compute slurm
```

Or, run with a different bulker environment for version-controlled software set management:

```
looper run --compute bulker_local
```

### Run just a few samples


Run only the first sample:
```
looper run --limit 1
```

Run only samples with a given name:

```
looper run --sel-attr sample_name --sel-incl frog_1
```

Exclude samples with a given name:

```
looper run --sel-attr sample_name --sel-excl frog_1
```

### Run multiple samples in one slurm job:

```
looper run --compute slurm --lumpn 2
```



