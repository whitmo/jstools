from ConfigParser import ConfigParser
from ConfigParser import NoSectionError
from jstools import utils, merge
from memoize import memoizedproperty
import logging
import pkg_resources

DIST = pkg_resources.Requirement.parse("jstools")

logger = logging.getLogger('jstools.deps')


class DepMap(ConfigParser):
    """
    dependency mapper
    """
    template = dict(require='// @requires %s\n',
                     include='// @include %s\n')
    
    def __init__(self, defaults=None, printer=logger):
        ConfigParser.__init__(self, defaults)
        self.printer = printer

    @memoizedproperty
    def alias_map(self):
        return utils.SectionMap(self, 'alias')
        
    @classmethod
    def from_resource(cls, resource_name, dist=DIST, defaults=None, printer=logger):
        conf = pkg_resources.resource_stream(dist, resource_name)
        dmap = cls(defaults=defaults, printer=printer)
        dmap.readfp(conf)
        return dmap

    @classmethod
    def from_path(cls, path, defaults=None, printer=logger):
        dmap = cls(defaults=defaults, printer=printer)
        if isinstance(path, basestring):
            path = path,
        paths = dmap.read(path)
        assert paths, ValueError("No valid config files: %s" %paths)
        return dmap

    @memoizedproperty
    def reverse_alias_map(self):
        return dict((v, k) for k, v in self.alias_map.items())
    
    def get_dependencies_by_filename(self, filename):
        alias = self.reverse_alias_map[filename]
        return self.get_dependencies_by_alias(alias)

    def get_dependencies_by_alias(self, alias):
        try:
            return utils.SectionMap(self, alias)
        except NoSectionError:
            return None
    
    get_deps = get_dependencies_by_alias

    def guess_alias_by_filename(self, filename, sorter=sorted, single=True):
        guesses = (self.reverse_alias_map.get(fn) for fn in sorter(self.reverse_alias_map.keys()) if fn.endswith(filename))
        
        if single:
            try:
                return guesses.next()
            except StopIteration:
                return None
        return guesses

    def formatted_dependencies(self, alias):
        for directive, aliases in self.get_deps(alias).items():
            for alias in aliases.split():
                try:
                    yield self.template[directive] %self.alias_map[alias]
                except KeyError:
                    raise AliasNotFound("Alias '%s' not found in %s. "
                                        "Check dependency cfg for alias mismatch." \
                                        %(alias, self.alias_map.keys()))

            
class AliasNotFound(KeyError):
    """
    Exception for any time an alias is not found
    """
