"""
build.py

Copyright (c) 2008 OpenGeo. All rights reserved.
"""
import sys
from jstools import DIST
from jstools.merge import Merger
from jstools.utils import arg_parser
import pkg_resources
import optparse
import os
import logging

logger = logging.getLogger('jstools.build')
curdir = os.path.abspath(os.curdir)

usage = "usage: %prog [options] filename1.cfg [filename2.cfg...]"
default_parser = optparse.OptionParser(usage=usage)
default_parser.add_option('-u', '--uncompress',
                  help="Don't compresses aggregated javascript",
                  action="store_true",
                  dest="uncompress",
                  default=False)
default_parser.add_option('-v', '--verbose',
                  help="print more info",
                  action="store_true",
                  dest="verbose",
                  default=False)
default_parser.add_option('-l', '--list-only',
                  help="Only list javascript files that would have been merged",
                  action="store_true",
                  dest="list_only",
                  default=False)
default_parser.add_option('-o', '--output',
                  help="Output directory (defaults to current directory)",
                  action="store",
                  dest="output_dir",
                  default=curdir)
default_parser.add_option('-r', '--resource',
                  help="resource base directory (for interpolation)",
                  action="store",
                  dest="resource_dir",
                  default=curdir)
default_parser.add_option('-b', '--base-dir',
                  help="base directory for root dirs (defaults to current directory)",
                  action="store",
                  dest="root_dir",
                  default=curdir)
default_parser.add_option('-j', '--just',
                  help="Only create file for this section",
                  action="store",
                  dest="single_file",
                  default=None)
default_parser.add_option('-s', '--single-file-build',
                  help="Create a single file of all of possible output",
                  action="store",
                  dest="concat",
                  default=None)
default_parser.add_option('-c', '--compressor',
                  help="Compressor plugin to use in form {specifier}:{'arguments_string'}",
                  action="store",
                  dest="compressor",
                  default="default")


@arg_parser(default_parser)
def default_merge(args=None, options=None, parser=None):
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    if len(args) > 1:
        filenames = args[1:]
    else:
        parser.error("You must provide at least one config filename")
    merger = Merger.from_fn(filenames,
                            output_dir=options.output_dir,
                            root_dir=options.root_dir,
                            defaults={'resource-dir':options.resource_dir},
                            printer=logger)
    out = merger.run(uncompressed=options.uncompress,
                     single=options.single_file,
                     concatenate=options.concat,
                     compressor=options.compressor,
                     list_only=options.list_only)
    logger.info("Done:")
    logger.info("\n".join(out))


def build():
    ep_map = pkg_resources.get_entry_map(DIST, "jstools.jsbuild_command")
    plugin = "default"
    command = ep_map.get(plugin).load()
    command()

