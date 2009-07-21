"""
Integration for creating sphinx compatible docs from javascript source
comments
"""
from ConfigParser import ConfigParser
from jinja2 import Template
from jstools import tsort
import os
import re

SUFFIX_JS = ".js"
SUFFIX_JST = ".jst"
SUFFIX_RST = ".rst"
DEFAULT_MARKER = "api"

_marker = object()


class DocParser(ConfigParser):

    def __init__(self, defaults=None):
        ConfigParser.__init__(self, defaults)

    @classmethod
    def from_fn(cls, fn, defaults=None):
        """Load up config files in our parser."""
        parser = cls(defaults)
        if isinstance(fn, basestring):
            fn = fn,
        fns = parser.read(fn)
        assert fns, ValueError("No valid config files: %s" % fns)
        return parser
    
    key_list = () 
    keys = 'root', 

    def make_cfg(self, section):
        cfg = dict(self.items(section))
        for key in self.key_list:
            val = cfg.setdefault(key, [])
            if isinstance(val, basestring):
                cfg[key]=[x for x in val.split() if not x.startswith('#')]
        for key in self.keys:
            cfg.setdefault(key, None)
        return cfg
    
    def run(self):
        sections = self.sections()
        # @@ how much of this is shared with merge.py?
        for section in sections:
            cfg = self.make_cfg(section)
            #@@ use logging
            print("Extracting docs for %s" % section)
            sourcedir = cfg['root']
            outdir = cfg['output']
            # gather data for each source file
            files = {}
            for root, dirs, entries in os.walk(sourcedir):
                for filename in entries:
                    if filename.endswith(SUFFIX_JS) and not filename.startswith("."):
                        filepath = os.path.join(root, filename)[len(sourcedir)+1:]
                        jsfile = SourceFile.from_filename(
                            os.path.join(sourcedir, filepath),
                            cfg)
                        if jsfile.data:
                            files[filepath] = jsfile
        
            # create dict of dependencies
            dependencies = {}
            for filepath, jsfile in files.items():
                dependencies[filepath] = jsfile.extends
            
            # extend data with any data from parents
            for filepath in tsort.sort(dependencies):
                jsfile = files[filepath]
                if jsfile.extends:
                    jsfile.inherit([files[parentpath] for parentpath in sorted(jsfile.extends, reverse=True) if parentpath in files])
                    
                # parse template for each file
                template_filename = os.path.join(sourcedir, filepath.split(SUFFIX_JS)[0] + SUFFIX_JST)
                if not os.path.exists(template_filename):
                    # throw something if template not given in config here
                    template_filename = cfg["template"]
                template = Template(open(template_filename, "U").read())
                out = template.render(jsfile.data)
                output_filename = os.path.join(outdir, filepath.split(SUFFIX_JS)[0] + SUFFIX_RST)
                output_dirname = os.path.dirname(output_filename)
                if not os.path.exists(output_dirname):
                    os.makedirs(output_dirname)
                f = open(output_filename, "w")
                f.write(out)
                f.close()

#@@ integrate with jstool.merge.SourceFile?
class SourceFile(object):
    """
    Represents a JavaScript source code file.
    """
    def __init__(self, source, options=None):
        self.source = source
        self.options = options
        self._data = _marker
        self._comments = _marker
        self._context = _marker
        self.extends = []
    
    @classmethod
    def from_filename(cls, filename, options=None):
        fh = open(filename, "U")
        source = fh.read()
        fh.close()
        return cls(source, options=options)
        
    @property
    def comments(self):
        if self._comments == _marker:
            comments = ()
            if self.options and "marker" in self.options:
                marker = self.options["marker"]
            else:
                marker = DEFAULT_MARKER
            for match in re.finditer(r'^\s*/\*\*\s*' + marker + '\s*:\s*(?P<comment>[\S\s]*?)\*+/', self.source, re.MULTILINE):
                comment = match.group('comment')
                lines = [re.sub(r'^\s*\*+', '', line.rstrip()) for line in comment.split('\n')]
                if len(lines) == 1:
                    label = "(define)"
                    block = lines[0].strip(),
                elif len(lines) > 1:
                    spaces = None
                    label = lines.pop(0)
                    block = ()
                    for line in lines:
                        if line and not line.isspace() and spaces is None:
                            spaces = len(line) - len(line.lstrip())
                        if spaces is not None:
                            if len(line) > spaces:
                                line = line[spaces:]
                            block += line,
                comments += dict(label=label, block=block),
            self._comments = comments
        return self._comments
    
    @property
    def data(self):
        if self._data == _marker:
            data = {}
            for comment in self.comments:
                label = comment["label"]
                block = comment["block"]
                if label.startswith("("):
                    if label == "(define)":
                        for defline in block:
                            m = re.match(r"\s*([\w\[\]]+)\s*=\s*(.*?)\s*$", defline)
                            if m:
                                self._add_data(data, m.group(1), m.group(2))
                    elif label == "(extends)":
                        self.extends = [path.strip() for path in block if path.strip()]
                else:
                    block = "\n".join(block)
                    self._add_data(data, label, block)
            if len(data) > 0:
                self._data = data
            else:
                self._data = None
        return self._data
    
    def _add_data(self, data, label, block):
        m = re.match(r"(\w+)\[(.*?)\]", label)
        if m:
            name = m.group(1)
            key = m.group(2)
            if len(key) > 0:
                # dictionary
                if not name in data:
                    data[name] = {}
                data[name][key] = block
            else:
                # list
                if not name in data:
                    data[name] = []
                data[name] += [block]
        else:
            data[label] = block
    
    def inherit(self, files):
        for obj in files:
            data = obj.data
            if "_parents" in self._data:
                self.data["_parents"].insert(0, data)
            else:
                self.data["_parents"] = [data]
            for key, value in data.items():
                if isinstance(value, list):
                    # concatenate with any existing list
                    if key in self._data:
                        self._data[key] += value
                    else:
                        self._data[key] = value[:]
                elif isinstance(value, dict):
                    # acquire values for keys we don't have already
                    value = value.copy()
                    if key in self._data:
                        value.update(self._data[key])
                    self._data[key] = value
                else:
                    if not key in self._data:
                        self._data[key] = value

def run():
    import sys
    DocParser.from_fn(sys.argv[1]).run()

if __name__ == '__main__':
    run()
