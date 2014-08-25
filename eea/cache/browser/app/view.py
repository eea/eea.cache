""" Browser
"""
import logging
from zope import event
from zope.component import queryAdapter, queryMultiAdapter
from plone.uuid.interfaces import IUUID
from eea.cache.event import InvalidateCacheEvent
from Products.Five.browser import BrowserView
from eea.cache.browser.interfaces import VARNISH

logger = logging.getLogger('eea.cache')

class InvalidateMemCache(BrowserView):
    """ View to invalidate memcache
    """
    def relatedItems(self, **kwargs):
        """ Invalidate related Items
        """
        getRelatedItems = getattr(self.context, 'getRelatedItems', lambda: [])
        for item in getRelatedItems():
            uid = queryAdapter(item, IUUID)
            if not uid:
                continue
            event.notify(InvalidateCacheEvent(raw=True, dependencies=[uid]))
        return 'Memcache invalidated for relatedItems'

    def backRefs(self, **kwargs):
        """ Invalidate back references
        """
        getBRefs = getattr(self.context, 'getBRefs', lambda: [])
        for item in getBRefs():
            uid = queryAdapter(item, IUUID)
            if not uid:
                continue
            event.notify(InvalidateCacheEvent(raw=True, dependencies=[uid]))
        return 'Memcache invalidated for back references'

    def __call__(self, **kwargs):
        uid = queryAdapter(self.context, IUUID)
        if not uid:
            return "Can't invalidate memcache. Missing uid adapter."
        event.notify(InvalidateCacheEvent(raw=True, dependencies=[uid]))
        return "Memcache invalidated"

class InvalidateCache(BrowserView):
    """ View to invalidate all cache varnish and memcache
    """

    def relatedItems(self, **kwargs):
        """ Invalidate related Items
        """
        getRelatedItems = getattr(self.context, 'getRelatedItems', lambda: [])
        for item in getRelatedItems():
            invalidate_cache = queryMultiAdapter(
                (item, self.request), name='cache.invalidate',
                default=lambda:None)
            invalidate_cache()
        return 'Cache invalidated for relatedItems'

    def backRefs(self, **kwargs):
        """ Invalidate back references
        """
        getBRefs = getattr(self.context, 'getBRefs', lambda: [])
        for item in getBRefs():
            invalidate_cache = queryMultiAdapter(
                (item, self.request), name='cache.invalidate',
                default=lambda:None)
            invalidate_cache()
        return 'Cache invalidated for back references'

    def __call__(self, **kwargs):

        # Memcache
        invalidate_memcache = queryMultiAdapter((self.context, self.request),
                                                name='memcache.invalidate')
        invalidate_memcache()

        # Varnish
        if not VARNISH:
            return "Cache invalidated"

        try:
            if VARNISH.purge.isPurged(self.context):
                event.notify(VARNISH.purge.Purge(self.context))
        except Exception, err:
            logger.exception(err)

        return "Cache invalidated"
