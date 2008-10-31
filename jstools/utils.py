"""
utils.py

Copyright (c) 2008 OpenGeo. All rights reserved.
"""

from decorator import decorator
import sys


def arg_parser(optparser):
    @decorator
    def caller(func, args=None, options=None, parser=None):
        if args is None and options is None:
            argv = sys.argv
            options, args = optparser.parse_args(argv)
        return func(args, options, optparser)
    return caller

def printer(verbosity):
    def _printer(txt, threshold=1):
        if int(verbosity) >= threshold:
            print txt
    return _printer
