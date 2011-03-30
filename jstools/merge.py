"""
merge.py

Copyright (c) 2008 OpenGeo. All rights reserved.
"""
from ConfigParser import ConfigParser
from jstools import REQ, DIST
from jstools import tsort
from StringIO import StringIO
from pprint import pprint
import logging
import os
import pkg_resources
import re


DEP_LINE = re.compile("^// @[include|requires]")
RE_INCLUDE = re.compile("@include (.*)\n")
RE_REQUIRE = re.compile("@requires (.*)\n")
SUFFIX_JAVASCRIPT = ".js"

_marker = object()
logger = logging.getLogger('jstools.merge')
special_section_prefixes = ["meta"]


class MissingImport(Exception):
    """Exception raised when a listed import is not found in the lib."""


class Exclude(object):
    def __init__(self, exclude):
        self.exclude = exclude
        self.pattern = None
        if exclude.startswith('r:'):
            self.pattern = re.compile(exclude[2:])

    def __eq__(self, other):
        if self.pattern is None:
            if self.exclude == other:
                return True
            else:
                # test other assuming self.exclude is a directory
                return other.startswith(self.exclude + \
                        ('' if self.exclude[-1]=='/' else '/'))
        else:
            return self.pattern.match(other) is not None


class Merger(ConfigParser):
    def __init__(self, output_dir, defaults=None, printer=logger):
        ConfigParser.__init__(self, defaults)
        self.output_dir = output_dir
        self.printer = printer
        
    @classmethod
    def from_fn(cls, fn, output_dir, defaults=None, printer=logger):
        """Load up a list of config filenames in our merger"""
        merger = cls(output_dir, defaults=defaults, printer=printer)
        if isinstance(fn, basestring):
            fn = fn,
        fns = merger.read(fn)
        assert fns, ValueError("No valid config files: %s" %fns)
        return merger

    @classmethod
    def from_resource(cls, resource_name, output_dir, requirement=REQ, defaults=None, printer=logger):
        conf = pkg_resources.resource_stream(requirement, resource_name)
        merger = cls(output_dir, defaults=defaults, printer=printer)
        merger.readfp(conf)
        return merger

    def make_sourcefile(self, sourcedir, filepath, exclude):
        self.printer.debug("Importing: %s" % filepath)
        return SourceFile(sourcedir, filepath, exclude)
    
    def merge(self, cfg, depmap=None):
        #@@ this function needs to be decomposed into smaller testable bits
        sourcedirs = cfg['root']

        # assemble all files in source directory according to config
        include = cfg.get('include', tuple())
        exclude = [Exclude(e) for e in cfg['exclude']]
        all_inc = cfg['first'] + cfg['include'] + cfg['last']
        files = {}
        implicit = False
        if not len(include):            
            # implicit file inclusion
            implicit = True

        for sourcedir in sourcedirs:
            newfiles = []
            for filepath in jsfiles_for_dir(sourcedir):
                fitem = filepath, srcfile = filepath, self.make_sourcefile(sourcedir, filepath, exclude),
                if implicit and not filepath in exclude:
                    all_inc.append(filepath)
                newfiles.append(fitem)

            newfiles = list((filepath, sf) for filepath, sf in newfiles if filepath in all_inc and filepath not in exclude)
            files.update(dict(newfiles))

        # ensure all @include and @requires references are in
        complete = False
        while not complete:
            complete = True
            for filepath, info in files.items():
                for path in info.include + info.requires:
                    if path not in exclude and not files.has_key(path):
                        complete = False
                        for sourcedir in sourcedirs:
                            if os.path.exists(os.path.join(sourcedir, path)):
                                files[path] = self.make_sourcefile(sourcedir, path, exclude)
                                break
                        else:
                            raise MissingImport("File '%s' not found in root directories" % path)
        
        # create list of dependencies
        dependencies = {}
        for filepath, info in files.items():
            dependencies[filepath] = info.requires

        
        # get tuple of files ordered by dependency
        self.printer.debug("Sorting dependencies.")
        order = [x for x in tsort.sort(dependencies)]

        # move forced first and last files to the required position
        self.printer.debug("Re-ordering files.")
        order = cfg['first'] + [item
                     for item in order
                     if ((item not in cfg['first']) and
                         (item not in cfg['last']))] + cfg['last']

        parts = ('first', 'include', 'last')
        required_files = []
        
        ## Make sure all imports are in files dictionary
        for part in parts:
            for fp in cfg[part]:
                if not fp in exclude and not files.has_key(fp):
                    raise MissingImport("File from '%s' not found: %s" % (part, fp))
        
        ## Header inserted at the start of each file in the output
        HEADER = "/* " + "=" * 70 + "\n    %s\n" + "   " + "=" * 70 + " */\n\n"

        ## Output the files in the determined order
        result = []
        for fp in order:
            f = files[fp]
            self.printer.debug("Exporting: " + f.filepath)
            result.append(HEADER % f.filepath)
            source = f.source
            result.append(source)
            if not source.endswith("\n"):
                result.append("\n")

        self.printer.debug("\nTotal files merged: %d " % len(files))
        merged = "".join(result)
        if cfg['closure']:
            merged = '(function(){%s})();' % merged
        return merged

    key_list = 'root', 'include', 'exclude', 'last', 'first', 
    keys = 'license', 'closure',

    def make_cfg(self, section):
        cfg = dict(self.items(section))
        for key in self.key_list:
            val = cfg.setdefault(key, [])
            if isinstance(val, basestring):
                cfg[key]=[x for x in val.split() if not x.startswith('#')]
        for key in self.keys:
            cfg.setdefault(key, None)
        return cfg

    def strip_deps(self, merged):
        #@@ make optional?
        return "\n".join(x for x in merged.split('\n') if not DEP_LINE.match(x))

    def compress(self, merged, plugin="default", cfg=None):
        self.printer.debug("Compressing with %s" %plugin)
        ep_map = pkg_resources.get_entry_map(DIST, "jstools.compressor")
        args = None
        func = ep_map.get(plugin).load()
        return func(merged, plugin, cfg)

    def do_section(self, section, cfg):
        header = "Building %s" % section
        self.printer.debug("%s\n%s" % (header, "-" * len(header)))
        merged = self.merge(cfg)
        if cfg.has_key('output'):
            outputfilename = cfg['output']
        else:
            outputfilename = os.path.join(self.output_dir, section)

##         if cfg['license']:
##             self.printer("Adding license file: %s" %cfg['license'])
##             merged = "\n".join((file(cfg['license']).read(), merged))
        return outputfilename, merged

    def js_sections(self):
        raw_sections = self.sections()
        if self.has_section("meta"):
            #@@ will need overhaul as soon as meta gets used for anything else
            # order the stuff someone cares about
            order = self.get("meta", "order").split()
            sections = [raw_sections.pop(raw_sections.index(index)) for index in order]
            # don't leave anything behind
            sections.extend(raw_sections)
            sections.remove('meta')
            return sections
        return raw_sections

    @staticmethod
    def fetch_license(cfg):
        license = ""
        if cfg['license']:
            license = file(cfg['license']).read()
            if not license.startswith("/*"):
                license = "/* %s */" %license
        return license

    def cat_run(self, outfile, sections, uncompressed=False, strip_deps=True, compressor='default'):
        newfiles = []
        cat = dict()
        lic = dict()
        for section in sections:
            cfg = self.make_cfg(section)
            outputfilename, merged = self.do_section(section, cfg)
            license = self.fetch_license(cfg)
            if license:
                lic[outputfilename] = license
            cat[outputfilename] = merged
            newfiles.append(outputfilename)
            
        outputfilename = os.path.join(self.output_dir, outfile)
        catted = StringIO()
        license = StringIO()
        seen = []
        for name in newfiles:
            print >> catted, cat[name]
            licout = lic[name]
            if licout not in seen: #slow?
                print >> license, licout
                seen.append(licout)


        merged = catted.getvalue()
        if not uncompressed:
            self.printer.debug("Compressing %s" %outputfilename)
            merged = self.compress(merged, compressor, self)
        elif strip_deps:
            merged = self.strip_deps(merged)
        merged_lic = license.getvalue()
        merged = "%s\n%s" %(merged_lic, merged)

        self.printer.info("Writing to %s (%d KB)" % (outputfilename, int(len(merged) / 1024)))
        sfb = file(outputfilename, "w").write(merged)
        newfiles = [outputfilename]
            
        return newfiles

    def nocat_run(self, sections, uncompressed=False, strip_deps=True, compressor='default'):
        newfiles = []

        for section in sections:
            cfg = self.make_cfg(section)
            license = self.fetch_license(cfg)

            outputfilename, merged = self.do_section(section, cfg)
            if not uncompressed:
                self.printer.debug("Compressing %s" %outputfilename)
                merged = self.compress(merged, compressor, self)
            elif strip_deps:
                merged = self.strip_deps(merged)
            self.printer.info("Writing to %s (%d KB)" % (outputfilename, int(len(merged) / 1024)))
            if license:
                self.printer.debug("Adding license file: %s" %cfg['license'])
                merged = "\n".join((license, merged))
            file(outputfilename, "w").write(merged)
                
            newfiles.append(outputfilename)
        return newfiles

    def run(self, uncompressed=False, single=None, strip_deps=True, concatenate=None, compressor="default"):
        sections = self.js_sections()
        if single is not None:
            assert single in sections, ValueError("%s not in %s" %(single, sections))
            sections = [single]
            
        if concatenate:
            return self.cat_run(concatenate, sections, uncompressed, strip_deps, compressor)
        else:
            return self.nocat_run(sections, uncompressed, strip_deps, compressor)



class SourceFile(object):
    """
    Represents a Javascript source code file.

    -- use depmap if given
    """

    def __init__(self, sourcedir, filepath, exclude, depmap=None):
        """
        """
        self.filepath = filepath
        self.exclude = exclude
        self.source = open(os.path.join(sourcedir, filepath), "U").read()
        self._requires = _marker
        self._include = _marker
        self.depmap = depmap

    @property
    def requires(self):
        """
        Extracts the dependencies specified in the source code and returns
        a list of them.
        """
        req = getattr(self, '_requires', None)
        if req is _marker:
            self._requires = [x.strip() for x in RE_REQUIRE.findall(self.source)\
                              if x not in self.exclude]
        return self._requires

    @property
    def include(self):
        """
        Extracts the list of files to be included before or after this one.
        """
        req = getattr(self, '_include', None)
        if req is _marker:
            self._include = [x.strip() for x in RE_INCLUDE.findall(self.source) \
                             if x not in self.exclude]
                                   
        return self._include


def jsfiles_for_dir(sourcedir, jssuffix=SUFFIX_JAVASCRIPT):
    for root, dirs, entries in os.walk(sourcedir):
        for filename in entries:
            if filename.endswith(jssuffix) and not filename.startswith("."):
                filepath = os.path.join(root, filename)[len(sourcedir)+1:]
                filepath = filepath.replace("\\", "/")
                yield filepath
