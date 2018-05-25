""" Browser
"""
import logging
from zope import event
from zope.component import queryAdapter, queryMultiAdapter
from plone.uuid.interfaces import IUUID
from eea.cache.event import InvalidateMemCacheEvent
from eea.cache.event import InvalidateVarnishEvent
from eea.cache.browser.interfaces import VARNISH
from eea.cache.config import EEAMessageFactory as _
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter


logger = logging.getLogger('eea.cache')

class BaseInvalidate(BrowserView):
    """ Base class for the invalidate
    """

    def __init__(self, context, request):
        super(BaseInvalidate, self).__init__(context, request)
        self._parent = None
        self._is_default_page = None

    @property
    def parent(self):
        if self._parent is None:
            self._parent = self.context.getParentNode()
        return self._parent

    @property
    def is_default_page(self):
        if self._is_default_page is None:
            state = getMultiAdapter((self.context, self.request),
                                    name='plone_context_state')
            self._is_default_page = state.is_default_page()
        return self._is_default_page


    def relatedItems(self, **kwargs):
        """ Invalidate related Items
        """
        msg = self.related_items(self.context)

        # Invalidate cache for a default view parent
        if self.is_default_page:
            msg = self.related_items(self.parent)

        return msg

    def backRefs(self, **kwargs):
        """ Invalidate back references
        """
        msg = self.back_refs(self.context)

        # Invalidate cache for a default view parent
        if self.is_default_page:
            msg = self.back_refs(self.parent)

        return msg

    def related_items(self, context, **kwargs):
        """ Related items invalidation. To be implemented
        """
        raise NotImplementedError

    def back_refs(self, context, **kwargs):
        """ Invalidate back references. To be implemented
        """
        raise NotImplementedError

class InvalidateMemCache(BaseInvalidate):
    """ View to invalidate memcache
    """

    def related_items(self, context, **kwargs):
        """ Invalidate related Items
        """
        getRelatedItems = getattr(self.context, 'getRelatedItems', lambda: [])
        for item in getRelatedItems():
            try:
                uid = queryAdapter(item, IUUID)
                if not uid:
                    continue
                event.notify(InvalidateMemCacheEvent(raw=True, dependencies=[uid]))
            except TypeError, err:
                logger.exception(err)
        return _(u"Memcache invalidated for relatedItems.")

    def back_refs(self, context, **kwargs):
        """ Invalidate back references
        """
        getBRefs = getattr(context, 'getBRefs', lambda r: [])
        for item in getBRefs('relatesTo'):
            try:
                uid = queryAdapter(item, IUUID)
                if not uid:
                    continue
                event.notify(InvalidateMemCacheEvent(raw=True, dependencies=[uid]))
            except TypeError, err:
                logger.exception(err)
        return _(u"Memcache invalidated for back references.")

    def invalidate_cache(self, context, **kwargs):
        uid = queryAdapter(context, IUUID)
        if not uid:
            return _(u"Can't invalidate memcache. Missing uid adapter.")
        event.notify(InvalidateMemCacheEvent(raw=True, dependencies=[uid]))
        return _(u"Memcache invalidated.")

    def __call__(self, **kwargs):
        msg = self.invalidate_cache(self.context)

        # Invalidate cache for a default view parent
        if self.is_default_page and not kwargs.get("parent", None):
            msg = self.invalidate_cache(self.parent)

        return msg


class InvalidateVarnish(BaseInvalidate):
    """ View to invalidate Varnish
    """

    def related_items(self, context, **kwargs):
        """ Invalidate related Items
        """
        getRelatedItems = getattr(context, 'getRelatedItems', lambda: [])
        for item in getRelatedItems():
            try:
                invalidate_cache = queryMultiAdapter(
                    (item, self.request), name='varnish.invalidate',
                    default=lambda: None)
                invalidate_cache()
            except TypeError, err:
                logger.exception(err)
        return _(u"Varnish invalidated for relatedItems.")

    def back_refs(self, context, **kwargs):
        """ Invalidate back references
        """
        getBRefs = getattr(context, 'getBRefs', lambda r: [])
        for item in getBRefs('relatesTo'):
            try:
                invalidate_cache = queryMultiAdapter(
                    (item, self.request), name='varnish.invalidate',
                    default=lambda: None)
                invalidate_cache()
            except TypeError, err:
                logger.exception(err)
        return _(u"Varnish invalidated for back references.")

    def invalidate_cache(self, context, **kwargs):
        """ Invalidate Varnish
        """
        if not VARNISH:
            return _(u"Varnish invalidated.")

        try:
            if VARNISH.purge.isPurged(context):
                event.notify(InvalidateVarnishEvent(context))
        except Exception, err:
            logger.exception(err)

        return _(u"Varnish invalidated.")

    def __call__(self, **kwargs):
        msg = self.invalidate_cache(self.context)

        # Invalidate cache for a default view parent
        if self.is_default_page and not kwargs.get("parent", None):
            msg = self.invalidate_cache(self.parent)

        return msg


class InvalidateCache(BaseInvalidate):
    """ View to invalidate Varnish and Memcache
    """

    def related_items(self, context, **kwargs):
        """ Invalidate related Items
        """
        getRelatedItems = getattr(self.context, 'getRelatedItems', lambda: [])
        for item in getRelatedItems():
            try:
                invalidate_cache = queryMultiAdapter(
                    (item, self.request), name='cache.invalidate',
                    default=lambda: None)
                invalidate_cache(parent="ignore")
            except TypeError, err:
                logger.exception(err)
        return _(u"Cache invalidated for relatedItems.")

    def back_refs(self, context, **kwargs):
        """ Invalidate back references
        """
        getBRefs = getattr(context, 'getBRefs', lambda r: [])
        for item in getBRefs('relatesTo'):
            try:
                invalidate_cache = queryMultiAdapter(
                    (item, self.request), name='cache.invalidate',
                    default=lambda: None)
                invalidate_cache(parent="ignore")
            except TypeError, err:
                logger.exception(err)
        return _(u"Cache invalidated for back references.")

    def invalidate_cache(self, context, **kwargs):
        """ Invalidate Varnish and Memcache
        """
        # Memcache
        invalidate_memcache = queryMultiAdapter((context, self.request),
                                                name='memcache.invalidate')
        invalidate_memcache(parent="ignore")

        # Varnish
        invalidate_varnish = queryMultiAdapter((context, self.request),
                                                name='varnish.invalidate')
        invalidate_varnish(parent="ignore")

        return _(u"Varnish and Memcache invalidated.")

    def __call__(self, **kwargs):
        msg = self.invalidate_cache(self.context)

        # Invalidate cache for a default view parent
        if self.is_default_page and not kwargs.get("parent", None):
            msg = self.invalidate_cache(self.parent)

        return msg
