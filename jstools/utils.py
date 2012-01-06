"""
utils.py

Copyright (c) 2008 OpenGeo. All rights reserved.
"""
from ConfigParser import NoSectionError
from ConfigParser import ConfigParser
from UserDict import DictMixin
import sys
import logging
import os
try:
    from functools import wraps
except ImportError:
    def wraps(f):
        def _decorator(func):
            def _wrapper(*args, **kwargs):
                func(*args, **kwargs)
            return _wrapper
        return _decorator

def arg_parser(optparser):
    "Allows for short circuiting of optparser"

    def wrapper(func):
        @wraps(func)
        def caller(args=None, options=None, parser=optparser):
            if args is None and options is None:
                argv = sys.argv
                options, args = optparser.parse_args(argv)
            return func(args, options, optparser)
        return caller
    return wrapper

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

def load_return(section=None):
    cp = ConfigParser()
    def load_file_or_section(path):
        cp.read(path)
        if section is not None:
            return SectionMap(cp, section)
        return cp
    return load_file_or_section

# for compressor
def retrieve_config(section=None, strict=False):
    # walk up from current directory
    # check virtualenv
    # check user directory
    # return either a ConfigParser or a SectionMap
    from paver.easy import path
    fn = ".jstools.cfg"
    conf = None
    directory = path(os.path.abspath(os.curdir))
    section_or_parser = load_return(section)
    while conf is None and directory:
        if os.path.exists(directory / fn):
            return section_or_parser(directory / fn)
        directory = directory.parent

    venv = os.environ.get("VIRTUAL_ENV")
    if venv and (path(venv) / fn).exists():
        return section_or_parser(path(venv) / fn)
    
    user = path(os.path.expanduser("~/"))
    if (user / fn).exists():
        return section_or_parser(user / fn)

