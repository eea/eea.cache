""" Browser
"""
import logging
from zope import event
from zope.component import queryAdapter, queryMultiAdapter
from plone.uuid.interfaces import IUUID
from eea.cache.event import InvalidateMemCacheEvent
from eea.cache.event import InvalidateVarnishEvent
from Products.Five.browser import BrowserView
from eea.cache.browser.interfaces import VARNISH
from eea.cache.config import EEAMessageFactory as _

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
            event.notify(InvalidateMemCacheEvent(raw=True, dependencies=[uid]))
        return _(u"Memcache invalidated for relatedItems.")

    def backRefs(self, **kwargs):
        """ Invalidate back references
        """
        getBRefs = getattr(self.context, 'getBRefs', lambda: [])
        for item in getBRefs():
            uid = queryAdapter(item, IUUID)
            if not uid:
                continue
            event.notify(InvalidateMemCacheEvent(raw=True, dependencies=[uid]))
        return _(u"Memcache invalidated for back references.")

    def __call__(self, **kwargs):
        uid = queryAdapter(self.context, IUUID)
        if not uid:
            return _(u"Can't invalidate memcache. Missing uid adapter.")
        event.notify(InvalidateMemCacheEvent(raw=True, dependencies=[uid]))
        return _(u"Memcache invalidated.")


class InvalidateVarnish(BrowserView):
    """ View to invalidate Varnish
    """

    def relatedItems(self, **kwargs):
        """ Invalidate related Items
        """
        getRelatedItems = getattr(self.context, 'getRelatedItems', lambda: [])
        for item in getRelatedItems():
            invalidate_cache = queryMultiAdapter(
                (item, self.request), name='varnish.invalidate',
                default=lambda: None)
            invalidate_cache()
        return _(u"Varnish invalidated for relatedItems.")

    def backRefs(self, **kwargs):
        """ Invalidate back references
        """
        getBRefs = getattr(self.context, 'getBRefs', lambda: [])
        for item in getBRefs():
            invalidate_cache = queryMultiAdapter(
                (item, self.request), name='varnish.invalidate',
                default=lambda: None)
            invalidate_cache()
        return _(u"Varnish invalidated for back references.")

    def __call__(self, **kwargs):
        if not VARNISH:
            return _(u"Varnish invalidated.")

        try:
            if VARNISH.purge.isPurged(self.context):
                event.notify(InvalidateVarnishEvent(self.context))
        except Exception, err:
            logger.exception(err)

        return _(u"Varnish invalidated.")


class InvalidateCache(BrowserView):
    """ View to invalidate Varnish and Memcache
    """

    def relatedItems(self, **kwargs):
        """ Invalidate related Items
        """
        getRelatedItems = getattr(self.context, 'getRelatedItems', lambda: [])
        for item in getRelatedItems():
            invalidate_cache = queryMultiAdapter(
                (item, self.request), name='cache.invalidate',
                default=lambda: None)
            invalidate_cache()
        return _(u"Cache invalidated for relatedItems.")

    def backRefs(self, **kwargs):
        """ Invalidate back references
        """
        getBRefs = getattr(self.context, 'getBRefs', lambda: [])
        for item in getBRefs():
            invalidate_cache = queryMultiAdapter(
                (item, self.request), name='cache.invalidate',
                default=lambda: None)
            invalidate_cache()
        return _(u"Cache invalidated for back references.")

    def __call__(self, **kwargs):
        # Memcache
        invalidate_memcache = queryMultiAdapter((self.context, self.request),
                                                name='memcache.invalidate')
        invalidate_memcache()

        # Varnish
        invalidate_varnish = queryMultiAdapter((self.context, self.request),
                                                name='varnish.invalidate')
        invalidate_varnish()

        return _(u"Varnish and Memcache invalidated.")
