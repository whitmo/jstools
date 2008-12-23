import tempfile
import os
from jstools import merge, deps, utils
import utils as testutils

libdir, tempdir = None, None

license = "### LICENSE ###"

def setup(mod):
    mod.tempdir, mod.libdir = testutils.setup_temp_dir()

def test_basic_config():
    merger = testutils.load_config('basic', libdir)
    handles = testutils.setup_dir(merger, prefix=libdir)
    depmap = deps.DepMap.from_resource("data/deps1.cfg")
    files = [x for x in testutils.inject_deps(handles, libdir, depmap)]


def xztest_basic_dependency_injection():
    merger = load_config('basic', libdir)
    handles = setup_dir(merger, prefix=libdir)
    depmap = deps.DepMap.from_resource("data/deps1.cfg")
    for fn in inject_deps(handles, libdir, depmap):
        print open(fn).readlines()
