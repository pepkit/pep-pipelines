#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

requirements:
  DockerRequirement:
    dockerPull: "quay.io/biocontainers/bwa:0.7.17--hed695b0_7"

inputs:
  InputFile1:
    type: File
    inputBinding:
      position: 201

  InputFile2:
    type: File
    inputBinding:
      position: 202

  Index:
    type: File
    inputBinding:
      position: 200
    secondaryFiles:
      - .amb
      - .ann
      - .bwt
      - .pac
      - .sa

baseCommand: [bwa, mem]

stdout: unsorted_reads.sam

outputs:
  reads_stdout:
    type: stdout
