""" EEA Cache package
"""
import os
from six.moves import cPickle as pickle
from hashlib import md5
from plone.memoize import volatile
from plone.memoize.interfaces import ICacheChooser
from plone.memoize.ram import AbstractDict
from plone.memoize.ram import store_in_cache
from plone.uuid.interfaces import IUUID
from eea.cache.utility import MemcachedClient
from eea.cache.interfaces import IMemcachedClient
import six

if six.PY3:
    unicode = str

try:
    from Products.CMFCore import interfaces
    IPropertiesTool = interfaces.IPropertiesTool
except ImportError:
    from zope.interface import Interface
    class IPropertiesTool(Interface):
        """ Fallback
        """
from zope.interface import directlyProvides
from zope.component import queryUtility, queryAdapter

class MemcacheAdapter(AbstractDict):
    """ Memcache Adapter
    """

    def __init__(self, client, globalkey=''):
        pt = queryUtility(IPropertiesTool)
        st = getattr(pt, 'site_properties', None)
        client_default = getattr(client, 'defaultLifetime', None)
        defaultLifetime = getattr(st, 'memcached_defaultLifetime',
                                  client_default)
        try:
            defaultLifetime = int(defaultLifetime)
        except Exception:
            defaultLifetime = client_default

        if getattr(client, 'defaultLifetime', None):
            client.defaultLifetime = defaultLifetime
        self.client = client

    def _make_key(self, source):
        """ Make key
        """
        key = source.encode('utf-8') if isinstance(source, unicode) else source
        return md5(key).hexdigest()

    def __getitem__(self, key):
        """ __getitem__
        """
        cached_value = None
        if getattr(self.client, 'query', None):
            cached_value = self.client.query(self._make_key(key), raw=True)
        if cached_value is None:
            raise KeyError(key)
        else:
            return pickle.loads(cached_value)

    def __setitem__(self, key, value):
        """ __setitem__
        """
        return self.set(key, value)

    def set(self, key, value, lifetime=None, dependencies=None):
        """ Set
        :param key: dict key
        :param value: dict value
        :param lifetime: cache lifetime
        :param dependencies: cache dependencies
        :return: None
        """
        dependencies = dependencies or []
        cached_value = pickle.dumps(value)
        if getattr(self.client, 'set', None):
            self.client.set(cached_value,
                            self._make_key(key),
                            lifetime=lifetime,
                            raw=True,
                            dependencies=dependencies)

def frontpageMemcached():
    """ Frontpage Memcached
    """
    servers = os.environ.get("MEMCACHE_SERVER",
                             "127.0.0.1:11211").split(",")
    return MemcachedClient(servers, defaultNS=u'frontpage')


def choose_cache(fun_name):
    """ Choose cache
    """
    client = queryUtility(IMemcachedClient)
    return MemcacheAdapter(client, globalkey=fun_name)


directlyProvides(choose_cache, ICacheChooser)

_marker = object()


def uuid(self=None, *args, **kwargs):
    """
    :param self: class or module where cache decorator was used
    :return: empty list or a list with one element containing object UID
    """
    context = getattr(self, 'context', self)
    return queryAdapter(context, IUUID)

def cache(get_key, dependencies=None, lifetime=None, auto_invalidate=True,
          cache_empty=False):
    """ Cache decorator

    :param get_key: a unique key to be used within cache
    :param dependencies: a list of strings used to bulk invalidate cache
    :param lifetime: time in seconds to be stored within cache
    :param auto_invalidate: invalidate cache when modified event is triggered
    :return: decorated function

    """
    def decorator(fun):
        """ Decorator
        """

        def replacement(*args, **kwargs):
            """ Replacement
            """
            try:
                key = get_key(fun, *args, **kwargs)
            except volatile.DontCache:
                return fun(*args, **kwargs)
            key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)
            cache_store = store_in_cache(fun, *args, **kwargs)
            cached_value = cache_store.get(key, _marker)
            if cached_value is _marker:
                cached_value = fun(*args, **kwargs)

                # #104478 avoid caching empty values by default
                # pass cache_empty=True if you want to cache empty results
                # ex: @cache(lambda *args, lifetime=3600, cache_empty=True)
                if not cached_value and not cache_empty:
                    return cached_value

                # plone.memoize doesn't have the lifetime keyword parameter
                # like eea.cache does so we check for set method
                if getattr(cache_store, 'set', None):
                    deps = dependencies or []
                    deps = deps[:]
                    if auto_invalidate:
                        uid = uuid(*args, **kwargs)
                        if uid and uid not in deps:
                            deps.append(uid)
                    cache_store.set(key, cached_value,
                                    lifetime=lifetime, dependencies=deps)
                else:
                    cache_store[key] = cached_value

            return cached_value
        return replacement
    return decorator
