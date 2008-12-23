import utils as testutils
from jstools import deps, merge
import pkg_resources
import os

libdir, tempdir = None, None

def file_tree(conf='basic', depcfg='data/deps1.cfg'):
    tempdir, libdir = testutils.setup_temp_dir()
    merger = testutils.load_config(conf, libdir)
    handles = testutils.setup_dir(merger, prefix=libdir)
    depmap = deps.DepMap.from_resource(depcfg)
    files = [x for x in testutils.inject_deps(handles, libdir, depmap)]
    merger.set('Output.js', 'root', libdir)
    license_path = os.path.join(libdir, "license.txt")
    merger.set('Output.js', 'license', license_path)
    license_file = open(license_path, 'w')
    print >> license_file, license; license_file.close()
    return merger

def test_circular_deps_config():
    merger = file_tree(depcfg="data/deps-circular.cfg")
    # eventually we may add some sort of "strict" checking
    # but for now, the merg should run
    assert merger.run(uncompressed=True, single='Output.js')

def test_exclude():
    """
    Exclude should trump all other declarations of dependency
    """
    merger = file_tree(conf='exclude')
    out = merger.run(uncompressed=True, single='Output.js', strip_deps=True)
    resfile = open(out[0])
    results = resfile.readlines()
    resfile.close()
    for ln in range(len(results)):
        # required
        assert 'prototype.js' not in results[ln], ValueError(results[ln])
        # included
        assert 'api.js' not in results[ln], ValueError(results[ln])


def test_merger_by_file():
    DIST = pkg_resources.Requirement.parse("jstools")
    filename = pkg_resources.resource_filename(DIST, "data/basic.cfg")
    assert merge.Merger.from_fn(filename, "/tmp")
    assert merge.Merger.from_fn([filename], "/tmp")
