""" Events
"""
from zope import interface
from zope import component
from eea.cache.interfaces import IInvalidateCacheEvent, IMemcachedClient

class InvalidateCacheEvent(object):
    """ invalidate cache event
    """
    interface.implements(IInvalidateCacheEvent)

    def __init__(self, cacheName=None, key=None,
                 ns=None, raw=False, dependencies=None):
        self.cacheName = cacheName
        self.key = key
        self.ns = ns
        self.raw = raw
        self.dependencies = dependencies or []

def invalidateCache(event):
    """ Invalidate cache
    """
    if event.cacheName is not None:
        cache = component.queryUtility(IMemcachedClient, event.cacheName)
        caches = []
        if cache is not None:
            caches.append(cache)
    else:
        caches = component.getAllUtilitiesRegisteredFor(IMemcachedClient)
    for cache in caches:
        if event.raw is not None:
            cache.invalidate(event.key, event.ns, event.raw, event.dependencies)
        else:
            cache.invalidate(event.key, event.ns, True, event.dependencies)
            cache.invalidate(event.key, event.ns, False, event.dependencies)

def flush(obj, evt):
    """ Purge memcache on ObjectModifiedEvent
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    invalidate = component.queryMultiAdapter((obj, request),
                     name=u'memcache.invalidate')
    if not invalidate:
        return

    return invalidate()


def flush_relatedItems(obj, evt):
    """ Purge memcache for all related items
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    invalidate = component.queryMultiAdapter((obj, request),
                     name=u'memcache.invalidate')
    if not invalidate:
        return

    return invalidate.relatedItems()

def flush_backRefs(obj, evt):
    """ Purge memcache for all back references
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    invalidate = component.queryMultiAdapter((obj, request),
                     name=u'memcache.invalidate')
    if not invalidate:
        return

    return invalidate.backRefs()
