"""
utils.py

Copyright (c) 2008 OpenGeo. All rights reserved.
"""
from ConfigParser import NoSectionError
from UserDict import DictMixin
from decorator import decorator
import sys
import logging

logger = logging.getLogger('jstools')

def arg_parser(optparser):
    @decorator
    def _caller(func, args=None, options=None, parser=None):
        if args is None and options is None:
            argv = sys.argv
            options, args = optparser.parse_args(argv)
        return func(args, options, optparser)
    return _caller

def printer(verbosity):
    def _printer(txt, threshold=1):
        if int(verbosity) >= threshold:
            logger.info(txt)
    return _printer


class SectionMap(DictMixin):
    def __init__(self, cp, section):
        if not cp.has_section(section):
            raise NoSectionError("%s does not exist in %s" %(section, cp))
        self.cp = cp
        self.section = section

    @property
    def section_items(self):
        return self.cp.items(self.section)
    
    def __getitem__(self, key):
        return dict(self.section_items)[key]

    def __delitem__(self, key):
        self.cp.remove_option(self.section, key)

    def __setitem__(self, key, value):
        self.cp.set(self.section, key, value)

    def keys(self):
        return dict(self.section_items).keys()
