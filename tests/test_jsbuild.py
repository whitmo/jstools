import utils as testutils
from jstools import deps
import os

libdir, tempdir = None, None



def setup(mod):
    mod.tempdir, mod.libdir = testutils.setup_temp_dir()

def file_tree():
    merger = testutils.load_config('basic', libdir)
    handles = testutils.setup_dir(merger, prefix=libdir)
    depmap = deps.DepMap.from_resource("data/deps-circular.cfg")
    files = [x for x in testutils.inject_deps(handles, libdir, depmap)]
    merger.set('Output.js', 'root', libdir)
    license_path = os.path.join(libdir, "license.txt")
    merger.set('Output.js', 'license', license_path)
    license_file = open(license_path, 'w')
    print >> license_file, license; license_file.close()
    return merger

def test_circular_deps_config():
    merger = file_tree()
    # eventually we may add some sort of "strict" checking
    # but for now, the merg should run
    assert merger.run(uncompressed=True, single='Output.js')

