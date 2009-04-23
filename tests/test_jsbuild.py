from jstools import deps, merge
import os
import pkg_resources
import re
import utils as testutils

R_FILES = re.compile(r"var filename='(.*)'")
libdir, tempdir = None, None

license = "### LICENSE ###\n"

def set_faux_files(cfg, libdir, *filenames):
    for fn in filenames:
        cfg.set(fn, 'root', libdir)
        license_path = os.path.join(libdir, "license.txt")
        cfg.set(fn, 'license', license_path)
        open(license_path, 'w').write(license)

def file_tree(conf='basic', depcfg='data/deps1.cfg', output_files=('Output.js',)):
    #@@ add a dep->out map option
    tempdir, libdir = testutils.setup_temp_dir()
    merger = testutils.load_config(conf, libdir)
    handles = testutils.setup_dir(merger, prefix=libdir)
    depmap = deps.DepMap.from_resource(depcfg)
    files = [x for x in testutils.inject_deps(handles, libdir, depmap)]
    set_faux_files(merger, libdir, *output_files)
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


def test_concatenate():
    """
    Passing Merger.run a concatenate kwarg should create a single
    """
    merger = file_tree(depcfg="data/concat-dep.cfg", conf="meta-concatenate", output_files=("Output1.js", "Output2.js", "Output3.js"))
    outfiles = merger.run(concatenate="sfb.js")
    sfb = open(outfiles[0])
    files_found = R_FILES.findall(sfb.read())
    assert files_found == ['core2/lib2.js', 'core3/lib3.js', 'core1/lib1.js']

    merger.add_section("meta")
    merger.set("meta", "order", "\n".join(['Output1.js', 'Output2.js', 'Output3.js']))
    outfiles = merger.run(concatenate="sfb2.js")
    sfb = open(outfiles[0])
    files_found = R_FILES.findall(sfb.read())
    assert files_found == ['core1/lib1.js', 'core2/lib2.js', 'core3/lib3.js']



def test_compression():
    pass
