# pep-pypiper
Example simple and bioinformatic pipelines using PEPs and pypiper.

## Simple pipeline

Here, we're counting lines using `wc`.

We can call it manually on a single file:
```
simple/pipelines/pypiper_wc.py --input simple/examples/rand1.txt -O simple/results/
```

Set env variable,e.g.  export TUTORIAL=/home/drc/GITHUB/pep-pipelines/pipelines/pep-pypiper/simple
Or, we can use `looper` to call it on one or many files:
```
looper run --looper-config examples/.looper.yaml --package local
```

## Bioinformatics pipeline

Here, we're aligning fastq files using `bowtie2`.  It also requires the `bowtie2_index` asset managed by `refgenie`.

Ensure, $REFGENIE is set e.g. export REFGENIE=/your/path/to/genome_config.yaml

We can also run this manually on a single sample:
```
bioinformatic/pipelines/pypiper_bowtie2.py --input bioinformatic/examples/paired/paired-end_1.fq.gz --genome hg38 --sample-name bowtie2_paired --single-or-paired paired -O simple/results/bowtie2/paired/results_pipeline -P 4 -M 4000 --input2 bioinformatic/examples/paired/paired/paired-end_2.fq.gz
```

Or on one to many samples using `looper`:
```
looper run --looper-config bioinformatic/examples/paired/.looper.yaml --package local
```


