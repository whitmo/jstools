"""
== from plone.memoize ==

Memo decorators for instances.

Stores values in an attribute on the instance. See instance.txt.

This package current subsumes memojito
"""

_marker = object()
class Memojito(object):
    propname = '_memojito_'
    def clear(self, inst):
        if hasattr(inst, self.propname):
            delattr(inst, self.propname)
        
    def clearbefore(self, func):
        def clear(*args, **kwargs):
            inst=args[0]
            self.clear(inst)
            return func(*args, **kwargs)
        return clear

    def clearafter(self, func):
        def clear(*args, **kwargs):
            inst=args[0]
            val = func(*args, **kwargs)
            self.clear(inst)
            return val 
        return clear

    def memoize(self, func):
        def memogetter(*args, **kwargs):
            inst = args[0]
            cache = getattr(inst, self.propname, _marker)
            if cache is _marker:
                setattr(inst, self.propname, dict())
                cache = getattr(inst, self.propname)

            # XXX this could be potentially big, a custom key should
            # be used if the arguments are expected to be big

            key = (func.__name__, args, frozenset(kwargs.items()))
            val = cache.get(key, _marker)
            if val is _marker:
                val=func(*args, **kwargs)
                cache[key]=val
                setattr(inst, self.propname, cache)
            return val
        return memogetter


_m = Memojito()
memoize = _m.memoize
clearbefore = _m.clearbefore
clearafter = _m.clearafter

def memoizedproperty(func):
    return property(_m.memoize(func))

__all__ = (memoize, memoizedproperty, clearbefore, clearafter)
