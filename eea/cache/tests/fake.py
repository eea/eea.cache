""" Fake
"""
from zope.interface import implements
from lovely.memcached.utility import MemcachedClient
from lovely.memcached.interfaces import IMemcachedClient

class FakeMemcachedClient(MemcachedClient):
    """ Fake Memcached Client
    """
    implements(IMemcachedClient)
    _cache = {}

    def invalidate(self, key=None, ns=None, raw=False, dependencies=None):
        """ Invalidate
        """
        for key, value in self._cache.items():
            if dependencies == value.get('dependencies'):
                del self._cache[key]
                return

    def query(self, key, default=None, ns=None, raw=False):
        """ Query
        """
        if key in self._cache.keys():
            return self._cache[key]['data']
        raise KeyError(key)

    def set(self, data, key, lifetime=None, ns=None,
            raw=False, dependencies=None):
        """ Set
        """
        if not dependencies:
            dependencies = []
        self._cache[key] = { 'data': data,
                             'dependencies': dependencies }
