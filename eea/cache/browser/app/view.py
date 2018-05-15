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


class InvalidateCacheFooter(InvalidateCache):
    """ Public view to invalidate Varnish and Memcache
    """

    def __call__(self, **kwargs):
        from Products.statusmessages.interfaces import IStatusMessage
        from zope.component import getMultiAdapter
        from Acquisition import aq_parent
        from Products.CMFCore.utils import getToolByName

        msg_invalidated = _(u"Cache invalidated.")
        msg_not_invalidated = _(u"Cache could not be invalidated.")

        # Get propper context for a default view
        self.parent = self.context
        state = getMultiAdapter((self.context, self.request), name='plone_context_state')
        if state.is_default_page():
            self.parent = aq_parent(self.context)

        # Don't allow invalidation with direct link
        referer = self.request.get('HTTP_REFERER', '')
        if referer.endswith('/'):
            referer = referer[:-1]
        if (self.context.absolute_url() != referer and
                    self.parent.absolute_url() != referer):
            return msg_not_invalidated

#        # Authenticated editors can invalidate cache from everywhere
#        mtool = getToolByName(self.context, 'portal_membership')
#        if mtool.checkPermission('Modify portal content', self.parent):
#            return True

#        # Check eea internal ips
#        addr_list = set(['127.0.0.1'])
#        ptool = getToolByName(self.context, 'portal_properties')
#        ips_list = getattr(ptool, 'eea_internal_ips', None)
#        if ips_list:
#            addr_list.update(ips_list.getProperty('allowed_ips', []))

#        addr = self.request.get('HTTP_X_FORWARDED_FOR', '')
#        addr = addr or self.request.get('REMOTE_ADDR', '')

#        for ip in addr_list:
#            if addr.startswith(ip):
#                return True
#        return False

        super(InvalidateCacheFooter, self).__call__(**kwargs)

        IStatusMessage(self.request).addStatusMessage(msg_invalidated, type='info')
        self.request.response.redirect(self.parent.absolute_url())
        return msg_invalidated