""" Browser
"""
from zope import event
from zope.component import queryAdapter
from plone.uuid.interfaces import IUUID
from eea.cache.event import InvalidateCacheEvent
from Products.Five.browser import BrowserView

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
