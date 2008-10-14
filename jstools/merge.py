from jstools import jsmin
from jstools import tsort
from ConfigParser import ConfigParser
import os
import re
import utils
    
SUFFIX_JAVASCRIPT = ".js"
RE_REQUIRE = re.compile("@requires (.*)\n") # TODO: Ensure in comment?
RE_INCLUDE = re.compile("@include (.*)\n")

_marker = object()

class Merger(ConfigParser):
    def __init__(self, output_dir, defaults=None, printer=lambda x: None):
        ConfigParser.__init__(self, defaults)
        self.output_dir = output_dir
        self.printer = printer
        
    @classmethod
    def from_fn(cls, fn, output_dir, defaults=None, printer=lambda x: None):
        """Load up a list of config filenames in our merger"""
        merger = cls(output_dir, defaults=defaults, printer=printer)
        if isinstance(fn, basestring):
            fn = fn,
        fns = merger.read(fn)
        assert fns, ValueError("No valid config files: %s" %fns)
        return merger        
        
    def merge(self, cfg):
        sourcedir = cfg['root']

        files = {}

        # assemble all files in source directory according to config
        include = cfg.get('include', False)
        for root, dirs, entries in os.walk(sourcedir):
            for filename in entries:
                if filename.endswith(SUFFIX_JAVASCRIPT) and not filename.startswith("."):
                    filepath = os.path.join(root, filename)[len(sourcedir)+1:]
                    filepath = filepath.replace("\\", "/")
                    if (include and filepath in
                            (cfg['first'] + cfg['include'] + cfg['last'])) or (
                            not include and filepath not in cfg['exclude']):
                        self.printer("Importing: %s" % filepath)
                        files[filepath] = SourceFile(sourcedir, filepath, cfg['exclude'])

        # ensure all @include and @requires references are in
        complete = False
        while not complete:
            complete = True
            for filepath, info in files.items():
                for path in info.include + info.requires:
                    if path not in cfg['exclude'] and not files.has_key(path):
                        complete = False
                        self.printer("Importing: %s" % path)
                        files[path] = SourceFile(sourcedir, path, cfg['exclude'])
        
        # create list of dependencies
        dependencies = {}
        for filepath, info in files.items():
            dependencies[filepath] = info.requires
        
        # get tuple of files ordered by dependency
        self.printer("Sorting dependencies.")
        order = tsort.sort(dependencies)

        # move forced first and last files to the required position
        self.printer("Re-ordering files.")
        order = cfg['first'] + [item
                     for item in order
                     if ((item not in cfg['first']) and
                         (item not in cfg['last']))] + cfg['last']


        ## Header inserted at the start of each file in the output
        HEADER = "/* " + "=" * 70 + "\n    %s\n" + "   " + "=" * 70 + " */\n\n"

        ## Output the files in the determined order
        result = []
        for fp in order:
            f = files[fp]
            self.printer("Exporting: " + f.filepath)
            result.append(HEADER % f.filepath)
            source = f.source
            result.append(source)
            if not source.endswith("\n"):
                result.append("\n")

        self.printer("\nTotal files merged: %d " % len(files))
        merged = "".join(result)
        if cfg['closure']:
            merged = '(function(){%s})();' % merged
        return merged

    key_list = 'include', 'exclude', 'last', 'first', 
    keys = 'license', 'root', 'closure',

    def make_cfg(self, section):
        cfg = dict(self.items(section))
        for key in self.key_list:
            val = cfg.setdefault(key, [])
            if isinstance(val, basestring):
                cfg[key]=[x for x in val.split() if not x.startswith('#')]
        for key in self.keys:
            cfg.setdefault(key, None)
        return cfg

    def run(self, uncompressed=False, single=None):
        sections = self.sections()
        if single is not None:
            assert single in sections, ValueError("%s not in %s" %(single, sections))
            sections = [single]
        newfiles = []
        for section in sections:
            cfg = self.make_cfg(section)
            header = "Building %s" % section
            self.printer("%s\n%s" % (header, "-" * len(header)))
            merged = self.merge(cfg)
            if not uncompressed:
                self.printer("Compressing...")
                merged = jsmin.jsmin(merged)
                
            if cfg.has_key('output'):
                outputfilename = cfg['output']
            else:
                outputfilename = os.path.join(self.output_dir, section)

            if cfg['license']:
                self.printer("Adding license file: %s" %cfg['license'])
                merged = file(cfg['license']).read() + merged

            self.printer("Writing to %s (%d KB).\n" % (outputfilename, int(len(merged) / 1024)))
            file(outputfilename, "w").write(merged)
            newfiles.append(outputfilename)
        return newfiles


class SourceFile(object):
    """
    Represents a Javascript source code file.
    """

    def __init__(self, sourcedir, filepath, exclude):
        """
        """
        self.filepath = filepath
        self.exclude = exclude
        self.source = open(os.path.join(sourcedir, filepath), "U").read()
        self._requires = _marker
        self._include = _marker

    @property
    def requires(self):
        """
        Extracts the dependencies specified in the source code and returns
        a list of them.
        """
        req = getattr(self, '_requires', None)
        if req is _marker:
            self._requires = filter(lambda x: x not in self.exclude,
                                    RE_REQUIRE.findall(self.source))
        return self._requires

    @property
    def include(self):
        """
        Extracts the list of files to be included before or after this one.
        """
        req = getattr(self, '_include', None)
        if req is _marker:
            self._include = filter(lambda x: x not in self.exclude,
                                   RE_INCLUDE.findall(self.source))
        return self._include


