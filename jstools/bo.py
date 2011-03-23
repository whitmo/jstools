"""
zc.buildout recipe
"""
from jstools import merge

class BuildJS(object):
    """
    @format for config
    """
    def __init__(self, buildout, name, options):
        self.defaults = defaults = {'resource-dir':options.get('resource-dir')}
        defaults.update(options)
        self.options = options
        self.buildout = buildout
        if options.get('output') is not None:
            #@@ detect if config only has 1 section
            assert options.get('only'), ValueError('output var requires "only" var to select config section')

        self.compress = options.get('compress', False)
        if self.compress != 'True' and self.compress != 'true':
            self.compress = False
        self.only = options.get('only')

    
    def install(self):
        self.merge = merge.Merger.from_fn(self.options.get('config'),
                                          output_dir=self.options.get('output-dir'),
                                          defaults=self.defaults,
                                          printer=self.buildout._logger)
        files = self.merge.run(uncompressed=not self.compress, single=self.only)
        return files

    update = install
