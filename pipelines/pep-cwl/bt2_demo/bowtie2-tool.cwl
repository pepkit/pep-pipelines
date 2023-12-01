#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool

requirements:
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  InitialWorkDirRequirement:
    listing: 
      - $(inputs.reference_index)
      - $(inputs.read1)
      - $(inputs.read2)
      - entryname: script.sh
        entry: |-
          ls $(inputs.reference_index_prefix)*

baseCommand: [bowtie2]
inputs:
  read1:
    type: File
    inputBinding:
      position: 1
      prefix: "-1"
  read2:
    type: File
    inputBinding:
      position: 2
      prefix: "-2"
  end_to_end_very_sensitive:
    type:
    - "null"
    - boolean
    inputBinding:
      position: 2
      prefix: '--very-sensitive'
  maxins:
    type:
    - int
    default: 2000
    inputBinding:
      position: 3
      prefix: "--maxins"
  rgid:
    type:
    - string
    default: "paired-end"
    inputBinding:
      position: 4
      prefix: "--rg-id"
  output_filename:
    type: string
    inputBinding:
      position: 90
      prefix: "-S"
    default: "test.bam"
    doc: |
      File for SAM output (default: stdout)
  reference_index_prefix:
    type:
    - string
  reference_index:
    doc: path to the FM-index files for the chosen reference genome
    type: File?
    secondaryFiles:
      - ^.1.bt2
      - ^.2.bt2
      - ^.3.bt2
      - ^.4.bt2
      - ^.rev.1.bt2
      - ^.rev.2.bt2
    inputBinding:
      position: 2
      prefix: "-x"
      valueFrom: $(self.path.replace(/\.fa/i,""))
  reference_index_folder:
    type: Directory?
    doc: "Folder with indices files"
    inputBinding:
      position: 81
      prefix: '-x'
      valueFrom: $(inputs.reference_index_prefix)
outputs: []

arguments:
  - valueFrom: $(inputs.reference_index_prefix.replace(/[^/]*$/,""))
    position: 90
    prefix: "-x"