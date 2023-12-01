#!/usr/bin/env python3
"""
wc pypiper pipeline
"""

__author__ = ["Jason Smith"]
__email__ = "jasonsmith@virginia.edu"
__version__ = "0.1"

from argparse import ArgumentParser
import sys
import os
import pypiper
from pypiper import build_command

###############################################################################
def parse_arguments():
    """
    Parse command-line arguments passed to the pipeline.
    """
    # Argument Parsing from yaml file.
    parser = ArgumentParser(description='wc pipeline version ' + __version__)
    
    # For convenience, add additional pypiper arguments by naming their
    # group. 
    # See: http://pypiper.databio.org/en/latest/cli/#pre-built-collections-of-arguments-added-via-groups
    parser = pypiper.add_pypiper_args(parser, groups=
        ['pypiper', 'common', 'looper'],
        required=["input", "output-parent"])

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
    file_name, ext = os.path.splitext(args.input[0])
    outfolder = os.path.abspath(
        os.path.join(args.output_parent, file_name))
    
    # Initialize, creating a global PipelineManager for
    # access in any ancillary functions outside of main().
    #   PipelineManager(): Constructor, initializes the pipeline.
    #   See: https://github.com/databio/pypiper/blob/67908f2ee5f51fa5fdddb67eb6d7891aefeeda6a/pypiper/manager.py#L63
    global pm
    pm = pypiper.PipelineManager(
        name="wc", outfolder=outfolder, args=args, version=__version__)

    # Now construct a shell command that the PipelineManger will execute.
    #   pypiper build_command(): Create a command from various parts.
    #   See: https://github.com/databio/pypiper/blob/49ceff6327fe0fa8a60d0b0a7d69d151d3efeab8/pypiper/utils.py#L65
    wc_cmd = build_command([
        "wc",
        "-l",
        args.input[0]
    ])

    # We'll capture the output of the shell command and report that as a
    # pipeline statistic.
    #   pypiper checkprint():
    #       Get a variable in python corresponding to the return value of the
    #       command you call. This is equivalent to running 
    #       subprocess.check_output().
    #   See: https://github.com/databio/pypiper/blob/67908f2ee5f51fa5fdddb67eb6d7891aefeeda6a/pypiper/manager.py#L805
    lc = pm.checkprint(wc_cmd)
    
    # pypiper report_result(): Writes a string to pipeline_stats_file.
    #   See: https://github.com/databio/pypiper/blob/67908f2ee5f51fa5fdddb67eb6d7891aefeeda6a/pypiper/manager.py#L1242
    pm.report_result("Line_count", lc)

    # And we're done so we stop the pipeline to complete gracefully.
    pm.stop_pipeline()

###############################################################################
if __name__ == '__main__':
    pm = None
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit("Pipeline aborted")