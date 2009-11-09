import os
import cPickle
import md5
from zope.interface import directlyProvides
from zope.component import queryUtility
from plone.memoize import volatile
from plone.memoize.interfaces import ICacheChooser
from plone.memoize.ram import AbstractDict
from plone.memoize.ram import store_in_cache
from lovely.memcached.utility import MemcachedClient
from lovely.memcached.interfaces import IMemcachedClient


DEPENDENCIES = { 'frontpage-highlights' : ['Products.EEAContentTypes.browser.frontpage.getHigh',
                                           'Products.EEAContentTypes.browser.frontpage.getMedium',
                                           'Products.EEAContentTypes.browser.frontpage.getLow'],
                 'navigation' : ['Products.NavigationManager.NavigationManager.getTree',],
                 'eea.facetednavigation': ['eea.facetednavigation.browser.app.query.__call__',
                                           'eea.facetednavigation.browser.app.counter.__call__',],
                 'eea.sitestructurediff': ['eea.sitestructurediff.browser.sitemap.data',],
                 }

class MemcacheAdapter(AbstractDict):
    def __init__(self, client, globalkey=''):
        self.client = client

        dependencies = []
        if globalkey:
            for k, v in DEPENDENCIES.items():
                if globalkey in v:
                    dependencies.append(k)

        self.dependencies = dependencies

    def _make_key(self, source):
        return md5.new(source).hexdigest()

    def __getitem__(self, key):
        cached_value = self.client.query(self._make_key(key), raw=True)
        if cached_value is None:
            raise KeyError(key)
        else:
            return cPickle.loads(cached_value)

    def __setitem__(self, key, value):
        cached_value = cPickle.dumps(value)
        self.client.set( cached_value, self._make_key(key), raw=True, dependencies=self.dependencies)

def frontpageMemcached():
    servers=os.environ.get(
        "MEMCACHE_SERVER", "127.0.0.1:11211").split(",")
    return MemcachedClient(servers, defaultNS=u'frontpage')

def choose_cache(fun_name):
    client = queryUtility(IMemcachedClient)
    return MemcacheAdapter(client, globalkey=fun_name)


directlyProvides(choose_cache, ICacheChooser)


_marker = object()
def cache(get_key, dependencies=None):
    def decorator(fun):
        def replacement(*args, **kwargs):
            if dependencies is not None:
                for d in dependencies:
                    deps = DEPENDENCIES.get(d, [])
                    method = "%s.%s" % (fun.__module__, fun.__name__)
                    if method not in deps:
                        deps.append(method)
                        DEPENDENCIES[d] = deps
            try:
                key = get_key(fun, *args, **kwargs)
            except volatile.DontCache:
                return fun(*args, **kwargs)
            key = '%s.%s:%s' % (fun.__module__, fun.__name__, key)
            cache = store_in_cache(fun, *args, **kwargs)
            cached_value = cache.get(key, _marker)
            if cached_value is _marker:
                cached_value = cache[key] = fun(*args, **kwargs)
            return cached_value
        return replacement
    return decorator
