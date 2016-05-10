""" Events
"""
from zope.interface import implementer
from zope import component
from eea.cache.interfaces import IMemcachedClient
from eea.cache.interfaces import IInvalidateMemCacheEvent
from eea.cache.interfaces import IInvalidateEverythingEvent
#
# Varnish
#
try:
    from plone.app.caching.purge import Purge
    InvalidateVarnishEvent = Purge
except ImportError:
    class InvalidateVarnishEvent(object):
        """ Fallback invalidation event for varnish
        """
        def __init__(self, obj, *args, **kwargs):
            self.object = obj


class InvalidateEvent(object):
    """ Abstract cache invalidation event
    """
#
# Memcache
#
@implementer(IInvalidateMemCacheEvent)
class InvalidateMemCacheEvent(InvalidateEvent):
    """ invalidate memcache event
    """
    def __init__(self, cacheName=None, key=None,
                 ns=None, raw=False, dependencies=None):
        self.cacheName = cacheName
        self.key = key
        self.ns = ns
        self.raw = raw
        self.dependencies = dependencies or []

# BBB
InvalidateCacheEvent = InvalidateMemCacheEvent


#
# Varnish and memcache
#
@implementer(IInvalidateEverythingEvent)
class InvalidateEverythingEvent(InvalidateEvent):
    """ Invalidation event for both varnish and memcache
    """
    def __init__(self, obj):
        self.object = obj


@component.adapter(IInvalidateMemCacheEvent)
def invalidateMemCache(event):
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

#
# Util event handlers
#
def flushVarnish(obj, evt):
    """ Purge memcache on ObjectModifiedEvent
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    invalidate = component.queryMultiAdapter((obj, request),
                     name=u'varnish.invalidate')
    if not invalidate:
        return

    return invalidate()

def flushMemcache(obj, evt):
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

# BBB
flush = flushMemcache

def flushEverything(obj, evt):
    """ Invalidate varnish and memcache
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    invalidate = component.queryMultiAdapter((obj, request),
                     name=u'cache.invalidate')
    if not invalidate:
        return

    return invalidate()

def flushRelatedItems(obj, evt, everything=True):
    """ Purge related items from memcache and varnish

    If everything is False, purge object only from memcache
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    if everything:
        invalidate = component.queryMultiAdapter((obj, request),
                                                name=u'cache.invalidate')
    else:
        invalidate = component.queryMultiAdapter((obj, request),
                                                name=u'memcache.invalidate')
    if invalidate:
        invalidate.relatedItems()

def flushBackRefs(obj, evt, everything=True):
    """ Purge back references from memcache and varnish.

    If everything is False, purge object only from memcache
    """
    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    if everything:
        invalidate = component.queryMultiAdapter((obj, request),
                                                name=u'cache.invalidate')
    else:
        invalidate = component.queryMultiAdapter((obj, request),
                                                name=u'memcache.invalidate')
    if invalidate:
        invalidate.backRefs()
