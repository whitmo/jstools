from jstools import utils
from paver.easy import path, info
import tempfile
import subprocess
import os


def compress(input, args, cfg):
    """
    writes input to a tempfile, then runs yuicompressor on the tempfile
    """
    paths = list(find_paths(args, cfg))

    f, tpath = tempfile.mkstemp(suffix=".js")
    open(tpath, "w+").write(input)

    arg_string = "java -jar %s --type=js %s" %(paths.pop(0), tpath)
    
    new_env = dict(os.environ)
    if len(paths):
        new_env['CLASSPATH'] = paths.pop()
    elif not new_env.has_key("CLASSPATH"):
        info("No CLASSPATH found in environment or configuration")

    proc = subprocess.Popen(arg_string.split(" "), stdout=subprocess.PIPE, env=new_env)
    out, err = proc.communicate()
    if err:
        raise OSError(err)
    path(tpath).unlink()
    return out


def find_paths(args, cfg, limit=False):
    """
    cascading lookup, first non null match wins
    
    arg: jarpath, None (assume environmental variable)
    arg: jarpath, classpath
    build config: jarpath, classpath
    user config: jarpath, classpath

    @@ set up doctest runner

    >>> from jstools import yuicompressor as yc
    >>> from ConfigParser import ConfigParser
    >>> cp = ConfigParser()
    >>> find_paths("yui", cp, limit=True)
    None, None,
    
    >>> find_paths("yui:/my/yui/jar", cp, limit=True)
    assert ret == "/my/yui/jar", None,

    >>> find_paths("yui:/my/yui/jar:/my/lib/jars", cp, limit=True)
    "/my/yui/jar", "/my/lib/jars",

    >>> find_paths("yui:/my/yui/jar:/my/lib/jars:/more/lib/jars", cp, limit=True)
    "/my/yui/jar", "/my/lib/jars:/more/lib/jars",

    >>> cp.add_section("meta")
    >>> cp.set("meta", "jarpath", "/conf/jarpath")
    >>> cp.set("meta", "classpath", "/conf/classpath")

    >>> find_paths("yui:/my/yui/jar", cp, limit=True)
    "/my/yui/jar", "/conf/classpath",

    >>> find_paths("yui", cp, limit=True)
    "/conf/classpath", "/conf/classpath",

    Lastly, if no jar or classpath is found in the build config or
    command line, we look for a global config file.  Paver's yui
    install must be run to insure this is setup.
     
    >>> find_paths("yui", ConfigParser(), limit=True)
    "/conf/classpath", "/conf/classpath",
    """

    path = None
    path = args.split(":")
    paths = dict(jarpath=None, classpath=None)
    if len(path) == 2:
        paths['jarpath']=path[1]
    elif len(path)==3:
        del path[0]
        jarpath = path.pop(0)
        classpath = ":".join(path)
        paths.update(dict(jarpath=jarpath,
                          classpath=classpath))
        
    if not all(paths.values()) and cfg.has_section("meta"):
        paths = nondestructive_populate(utils.SectionMap(cfg, "meta"), paths)

    if limit:
        # mainly for testing purposes
        return paths
    
    # move to implicit options
    if not all(paths.values()):
        gc = utils.retrieve_config("yui_compressor")
        if gc is not None:
            paths = nondestructive_populate(gc, paths)
    
    return paths['jarpath'], paths['classpath'],

def nondestructive_populate(valmap, path_map):
    for key in path_map.keys():
        if not path_map.get(key):
            path_map[key] = valmap.get(key)
    return path_map





