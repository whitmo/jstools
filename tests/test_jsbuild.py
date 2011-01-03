from jstools import deps, merge, DIST, REQ
from ConfigParser import ConfigParser
import os
import pkg_resources
import re
import utils as testutils
from jstools.yuicompressor import find_paths
import os

R_FILES = re.compile(r"var filename='(.*?/.*?)';")
libdir, tempdir = None, None

license = "/* ### LICENSE ### */"
license2 = "### LICENSE2 ###"

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


def results_from_uncompressed_outfile(fp):
    resfile = open(fp)
    results = (x.strip() for x in resfile.readlines())
    results = (R_FILES.match(x) for x in results if x.startswith('var'))
    try:
        return [x.groups()[0] for x in results]
    finally:
        resfile.close()


def test_implicit():
    """
    If not an 'include' directive is not given, all files in the
    source directly should be added if not specified in the 'exclude'
    section.
    """
    merger = file_tree()
    merger.remove_option('Output.js', 'first')
    merger.remove_option('Output.js', 'last')

    out = merger.run(uncompressed=True, single='Output.js', strip_deps=True)
    results = results_from_uncompressed_outfile(out[0])
    assert results == ['3rd/prototype.js', 'core/application.js', 'core/api.js', 'core/params.js']
    assert not '3rd/logger.js' in results


def test_implicit_just_last():
    """
    Running against 'data/basic.cfg' w/out any first entries, all files
    should be picked up, but 'core/api.js' should be last.
    """
    merger = file_tree()
    merger.remove_option('Output.js', 'first')

    out = merger.run(uncompressed=True, single='Output.js', strip_deps=True)
    results = results_from_uncompressed_outfile(out[0])
    assert_basic_order(results)

    assert results[-1] == 'core/api.js'
    assert not '3rd/logger.js' in results


def assert_basic_order(results):
    """
    when deps are 'data/deps1.cfg' and first or last is specified as
    basic.cfg, output order should be:

    ['3rd/prototype.js',
    'core/application.js',
    'core/params.js',
    'core/api.js']
    
    """
    assert results == ['3rd/prototype.js',
                       'core/application.js',
                       'core/params.js',
                       'core/api.js'], results


def test_implicit_just_first():
    """
    Running against 'data/basic.cfg' w/out any last entries, all files
    should be picked up, but '3rd/prototype.js' should be first and
    'core/params.js' should be third.
    """
    merger = file_tree()
    merger.remove_option('Output.js', 'last')

    out = merger.run(uncompressed=True, single='Output.js', strip_deps=True)
    results = results_from_uncompressed_outfile(out[0])

    #@@ sorting actually hides valuable info here
    assert_basic_order(results)
    assert results[0] == '3rd/prototype.js'
    assert results[2] == 'core/params.js'
    assert not '3rd/logger.js' in results    


def test_merger_by_file():
    DIST = pkg_resources.Requirement.parse("jstools")
    filename = pkg_resources.resource_filename(DIST, "data/basic.cfg")
    assert merge.Merger.from_fn(filename, "/tmp")
    assert merge.Merger.from_fn([filename], "/tmp")


def test_concatenate():
    """
    Passing Merger.run a concatenate kwarg should create a single file
    """
    merger = file_tree(depcfg="data/concat-dep.cfg", conf="meta-concatenate", output_files=("Output1.js", "Output2.js", "Output3.js"))

    # set o2 to an alternate license
    lp = merger.get('Output2.js', 'license') + "2"
    merger.set('Output2.js', 'license', lp)
    open(lp, 'w').write(license2)

    outfiles = merger.run(concatenate="sfb.js")
    sfb = open(outfiles[0])
    out = sfb.read()
    files_found = R_FILES.findall(out)
    assert files_found == ['core2/lib2.js', 'core3/lib3.js', 'core1/lib1.js']

    assert license in out
    assert license2 in out

    merger.add_section("meta")
    merger.set("meta", "order", "\n".join(['Output1.js', 'Output2.js', 'Output3.js']))
    outfiles = merger.run(concatenate="sfb2.js")
    sfb = open(outfiles[0])
    files_found = R_FILES.findall(sfb.read())
    assert files_found == ['core1/lib1.js', 'core2/lib2.js', 'core3/lib3.js']




#@@ fragile 
jsmin_result = """
/* ### LICENSE ### */
(function(){window.NameSpace={};var long_internal_var=[1,2,3,4];var long_internal_var2=[long_internal_var,long_internal_var];window.NameSpace.extra_var=long_internal_var2;})();Namespace.Node={class_var:5,api_method:function(some_argument){var long_name_var=some_argument+1;return long_name_var;},api_method2:function(some_argument){return this.api_method(some_argument)+this.class_var;}};
"""

def compression_setup():
    merger = file_tree(conf='compress')
    js = pkg_resources.resource_string(REQ, "data/compress.js")
    open(os.path.join(testutils.libdir, "compress.js"), "w+").write(js)
    return merger

    
def test_default_compression():
    # jsmin default
    merger = compression_setup()
    outfiles = merger.run()
    sfb = open(outfiles[0]).read().strip()
    assert sfb == jsmin_result.strip(), sfb


#@@ fragile 
yui_result_noargs = """
/* ### LICENSE ### */
(function(){window.NameSpace={};var b=[1,2,3,4];var a=[b,b];window.NameSpace.extra_var=a})();Namespace.Node={class_var:5,api_method:function(b){var a=b+1;return a},api_method2:function(a){return this.api_method(a)+this.class_var}};
"""

def test_yui_compression():
    merger = compression_setup()
    for path in find_paths("yui", merger):
        path = path.split(":")
        if not os.path.exists(path[0]):
            raise ValueError("You must run 'paver get_yuicomp' to setup for this test")
    # yui no args: requires a default instance of yui available
    outfiles = merger.run(compressor="yui")

    sfb = open(outfiles[0]).read().strip()
    assert sfb == yui_result_noargs.strip(), sfb


def test_license_wrapping():
    """
    Licenses unwrapped by comment should get wrapped
    """
    merger = compression_setup()
    lp = merger.get('Output.js', 'license')
    open(lp, 'w').write(license2)
    outfiles = merger.run()
    sfb = open(outfiles[0]).read().strip()
    assert sfb.startswith("/*")


