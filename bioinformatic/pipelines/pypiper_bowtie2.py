#!/usr/bin/env python3
"""
bowtie2 pypiper pipeline
"""

__author__ = ["Jason Smith"]
__email__ = "jasonsmith@virginia.edu"
__version__ = "0.1"

from argparse import ArgumentParser
import os
import sys
import pypiper
from pypiper import build_command
from refgenconf import RefGenConf as RGC, select_genome_config

def parse_arguments():
    """
    Parse command-line arguments passed to the pipeline.
    """
    # Argument Parsing from yaml file.
    parser = ArgumentParser(description='bowtie2 pipeline version ' +
                            __version__)
                            
    # For convenience, add additional pypiper arguments by group. 
    #   See: http://pypiper.databio.org/en/latest/cli/#pre-built-collections-of-arguments-added-via-groups
    parser = pypiper.add_pypiper_args(parser, groups=
        ['pypiper', 'looper', 'ngs'],
        required=["input", "genome", "sample-name", "output-parent"])

    # Pipeline-specific arguments.
    parser.add_argument("-V", "--version", action="version",
                        version="%(prog)s {v}".format(v=__version__))

    args = parser.parse_args()

    if not args.input:
        parser.print_help()
        raise SystemExit

    return args
    
###############################################################################
def main():
    """
    Main pipeline process.
    """

    args = parse_arguments()
    
    # Create output folder.
    outfolder = os.path.abspath(
        os.path.join(args.output_parent, args.sample_name)) 
    
    # Initialize, creating global PipelineManager for
    #   access in ancillary functions outside of main().
    #   PipelineManager(): Constructor, initializes the pipeline.
    #   See: https://github.com/databio/pypiper/blob/67908f2ee5f51fa5fdddb67eb6d7891aefeeda6a/pypiper/manager.py#L63
    global pm
    pm = pypiper.PipelineManager(
        name="bowtie2", outfolder=outfolder, args=args, version=__version__)

    # Set paired end status.
    args.paired_end = args.single_or_paired.lower() == "paired"
    
    # Confirm paired end status was set if two input files are provided.
    if args.input2 and not args.paired_end:
        err_msg = ("Incompatible settings: You specified single-end, " + 
                   "but provided --input2.")
        pm.fail_pipeline(RuntimeError(err_msg))
    
    # Create convenience aliases.
    tools = pm.config.tools
    res = pm.config.resources
    unmap_fq1 = args.input[0]   
    if args.paired_end:
        unmap_fq2 = args.input2[0]
    
    # Create a refgenconf object to access genome assets.
    #   See: http://refgenie.databio.org/en/latest/refgenconf/
    #   This path to the "genome_config" file is established in the pipeline
    #   configuration file. The companion "py_bowtie2.yaml" file.
    rgc = RGC(select_genome_config(res.get("genome_config")))
    
    ############################################################################
    #                               Map to genome                              #
    ############################################################################

    # Log the start of alignment.
    pm.timestamp("### Map to genome")
    
    # Construct the path to the mapped file.
    mapped_sam = os.path.join(outfolder, args.sample_name + ".sam")
        
    # Grab the path to the bowtie2 index managed by Refgenie.
    genome_index = rgc.seek(args.genome_assembly, "bowtie2_index")
    # Ensure the path is compatible with bowtie2.
    if not genome_index.endswith(args.genome_assembly):
        genome_index = os.path.join(
            os.path.dirname(rgc.seek(args.genome_assembly, "bowtie2_index")),
            args.genome_assembly)
    
    # Add bowtie2 parameters.
    bt2_options = "--very-sensitive"
    if args.paired_end:
        bt2_options += " -X 2000"
    
    # Construct the base bowtie2 command which the PipelineManager will run.
    #   pypiper build_command(): Create a command from various parts.
    #   See: https://github.com/databio/pypiper/blob/49ceff6327fe0fa8a60d0b0a7d69d151d3efeab8/pypiper/utils.py#L65
    bt2_cmd = build_command([
        tools.bowtie2,
        ("-p", str(pm.cores)),
        bt2_options,
        ("--rg-id ", args.sample_name),
        ("-x", genome_index),
    ])

    # Add custom arguments for paired end or single end input data.
    if args.paired_end:
        bt2_cmd += " -1 " + unmap_fq1 + " -2 " + unmap_fq2
    else:
        bt2_cmd += " -U " + unmap_fq1

    # Add bowtie2 output file path.
    bt2_cmd += " > " + mapped_sam
    
    # Run the command and include the expected target. If you provide a 
    # target file, then pypiper will first check to see if that target exists,
    # and only run the command if the target does not exist.
    pm.run(bt2_cmd, mapped_sam)
    
    # To finalize we'll stop the pipeline to complete gracefully.
    pm.stop_pipeline()

###############################################################################
if __name__ == '__main__':
    pm = None
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit("Pipeline aborted")