from jstools import merge
import os
import tempfile

libdir, tempdir = None, None

def load_config(config_name, outputdir, defaults=None):
    if not config_name.endswith('.cfg') or config_name.endswith('.ini'):
        config_name += '.cfg'
    return merge.Merger.from_resource("data/" + config_name, outputdir, defaults=defaults)

def setup_dir(cp, which=None, prefix=None):
    care = ["exclude", "first", "last", "include"]
    handles = []
    if which is None:
        for sect in cp.sections():
            handles.extend(setup_dir(cp, which=sect, prefix=prefix))

        return handles

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
    fileh = open(fpath, "wr")
    print >> fileh, "var filename='%s';" %filename.strip()
    fileh.close()
    return fileh

def get_contents(path):
    fi = open(path)
    try:
        return fi.readlines()
    finally:
        fi.close()

def write_deps(formatted_deps, filename):
    lines = get_contents(filename)
    lines.insert(0, formatted_deps)
    fh = open(filename, 'w')
    fh.writelines(lines)
    fh.close()

def inject_deps(handles, libdir, depmap):
    pmap = dict((x.name.split("/")[-1], x.name) for x in handles)
    for fn in pmap.keys():
        alias = depmap.guess_alias_by_filename(fn)
        if alias is None:
            continue

        if not depmap.get_deps(alias):
            continue

        for fd in depmap.formatted_dependencies(alias):
            write_deps(fd, pmap[fn])
        yield pmap[fn]

def setup_temp_dir():
    global libdir, tempdir
    tempdir = tempfile.mkdtemp('jstools-')
    libdir = os.path.join(tempdir, "lib")
    os.mkdir(libdir)
    return tempdir, libdir
