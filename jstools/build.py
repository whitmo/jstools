"""
build.py

Copyright (c) 2008 OpenGeo. All rights reserved.
"""

from jstools.merge import Merger
from jstools.utils import arg_parser, printer as printer_factory
import optparse
import os

curdir = os.path.abspath(os.curdir)
usage = "usage: %prog [options] filename1.cfg [filename2.cfg...]"
parser = optparse.OptionParser(usage=usage)
parser.add_option('-u', '--uncompress',
                  help="Don't compresses aggregated javascript",
                  action="store_true",
                  dest="uncompress",
                  default=False)
parser.add_option('-v', '--verbose',
                  help="print more info",
                  action="store_true",
                  dest="verbose",
                  default=False)
parser.add_option('-o', '--output',
                  help="Output directory",
                  action="store",
                  dest="output_dir",
                  default=curdir)
parser.add_option('-r', '--resource',
                  help="resource base directory (for interpolation)",
                  action="store",
                  dest="resource_dir",
                  default=curdir)
parser.add_option('-s', '--single',
                  help="Only create file for this section",
                  action="store",
                  dest="single_file",
                  default=None)
        
#@@ test 
@arg_parser(parser)
def build(args=None, options=None, parser=None):
    printer = printer_factory(options.verbose)
    if len(args) > 1:
        filenames = args[1:]
    else:
        parser.error("You must provide at least one config filename")
    merger = Merger.from_fn(filenames,
                            output_dir=options.output_dir,
                            defaults={'resource-dir':options.resource_dir},
                            printer=printer)
    out = merger.run(uncompressed=options.uncompress, single=options.single_file)
    printer("Done: %s" %out, 0)


