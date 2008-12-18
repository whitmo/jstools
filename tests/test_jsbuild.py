import tempfile
import os
from jstools import merge

class bag(object):
    pass


libdir, tempdir = None, None

license = "### LICENSE ###"

def setup(mod):
    global libdir, tempdir
    tempdir = tempfile.mkdtemp('jstools-')
    libdir = os.path.join(tempdir, "lib")
    os.mkdir(libdir)

def load_config(config_name, outputdir, defaults=None):
    if not config_name.endswith('.cfg') or config_name.ends_with('.ini'):
        config_name += '.cfg'
    return merge.Merger.from_resource("data/" + config_name, outputdir, defaults=defaults)

def setup_dir(cp, which=None, prefix=None):
    care = ["exclude", "first", "last", "include"]
    handles = []
    if which is None:
        for sect in cp.sections():
            handles.extend(setup_dir(cp, which=sect))
        return handles

    if prefix is None:
        prefix = libdir

    filenames = dict(item for item in cp.items(which) if item[0] in care)

    for fn in filenames.values():
        fnames = fn.split("\n")
        h = [mkdir_file(name, prefix) for name in fnames if name]
        handles.extend(h)
    return handles

def mkdir_file(filename, prefix=""):
    filename = filename.strip()
    names = filename.split("/")
    path, js = names[:-1], names[-1] 
    assert js.endswith('js')
    path = os.path.join(prefix, "/".join(path))
    assert not path.endswith('js')
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno != 17:
            raise
    fpath = os.path.join(prefix, filename)
    fileh = open(fpath, "w")
    print >> fileh, "var filename='%s';" %filename.strip()
    return fileh

def test_basic_config():
    merger = load_config('basic', libdir)
    handles = setup_dir(merger)


