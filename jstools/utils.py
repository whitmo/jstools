"""
utils.py

Copyright (c) 2008 OpenGeo. All rights reserved.
"""
from ConfigParser import NoSectionError
from UserDict import DictMixin
import sys
import logging
import os
try:
    from functools import wraps
except ImportError:
    wraps = lambda func: func

logger = logging.getLogger('jstools')

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

# for compressor
def retrieve_config(section=None, strict=False):
    # first local
    # then env
    # then user
    fn = ".jstools.cfg"
    venv = os.environ.get("VIRTUAL_ENV")
    user = os.path.join(os.path.expanduser("~/"), fn)
    if venv is not None:
        venv = os.path.join(venv, fn)
    possible = fn, venv, user,
    valid_path = None
    cp = ConfigParser()
    for path in (path for path in possible if path):
        if os.path.exists(path):
            valid_path = path
            cp.read([valid_path])
            if section not in cp.sections():
                continue
            break

    if valid_path is None:
        if strict:
            raise ValueError("Configuration Not Found")
        else:
            return




            

    
