""" Browser
"""
from zope import schema
from z3c.form import form, button
from zope.interface import implements
from zope.component import adapts, queryMultiAdapter
from plone.supermodel import model
from plone.autoform.form import AutoExtensibleForm
from eea.cache.interfaces import ICacheAware
from eea.cache.browser.interfaces import VARNISH
from eea.cache.config import EEAMessageFactory as _


class ISettings(model.Schema):
    """ Cache settings
    """
    memcache = schema.Bool(
        title=_(u"Memcache"),
        description=_(u"Invalidate Memcache cache."),
        required=False,
        default=False
    )

    if VARNISH:
        varnish = schema.Bool(
            title=_(u"Varnish"),
            description=_(u"Invalidate Varnish cache."),
            required=False,
            default=False
        )

    relatedItems = schema.Bool(
        title=_(u"Related items"),
        description=_(u"Also invalidate cache for context's related items."),
        required=False,
        default=False
    )

    backRefs = schema.Bool(
        title=_(u"Back references"),
        description=_(u"Also invalidate cache for context's back references."),
        required=False,
        default=False
    )


class SettingsBehavior(object):
    implements(ISettings)
    adapts(ICacheAware)

    def __init__(self, context):
        self.context = context

    @property
    def memcache(self):
        """ Memcache
        """
        return False

    @memcache.setter
    def memcache(self, value):
        """ Invalidate memcache?
        """
        print "memcache %s" % value

    @property
    def varnish(self):
        """ Varnish
        """
        return False

    @varnish.setter
    def varnish(self, value):
        """ Invalidate varnish?
        """
        print "varnish %s" % value

    @property
    def relatedItems(self):
        """ Related items
        """
        return False

    @relatedItems.setter
    def relatedItems(self, value):
        """ Invalidate related items?
        """
        print "related items %s" % value

    @property
    def backRefs(self):
        """ Back references
        """
        return False

    @backRefs.setter
    def backRefs(self, value):
        """ Invalidate back references?
        """
        print "back refs %s" % value


class SettingsForm(AutoExtensibleForm, form.EditForm):
    """ Cache settings
    """
    schema = ISettings

    def invalidateRelated(self, invalidate_adaptor, data):
        """ Invalidate related items and back references
        """
        if data.get('relatedItems', False):
            self.status += u" " + invalidate_adaptor.relatedItems()

        if data.get('backRefs', False):
            self.status += u" " + invalidate_adaptor.backRefs()

    @button.buttonAndHandler(_('Invalidate'), name='invalidate')
    def invalidate(self, action):
        """ Invalidate cache
        """
        self.status = u""
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        content = self.getContent()
        changes = form.applyChanges(self, content, data)
        if changes:
            self.status = _(u"Cache invalidated")
        else:
            self.status = _(u"Nothing selected to invalidate")

        # if data.get('varnish', False):
        #     invalidate = queryMultiAdapter((self.context, self.request),
        #                                    name='varnish.invalidate')
        #     if invalidate:
        #         self.status += u" " + invalidate()
        #         self.invalidateRelated(invalidate, data)
        #     else:
        #         self.status += u" Adapter missing, can't invalidate Varnish."
        #
        # if data.get('memcache', False):
        #     invalidate = queryMultiAdapter((self.context, self.request),
        #                                    name='memcache.invalidate')
        #     if invalidate:
        #         self.status += u" " + invalidate()
        #         self.invalidateRelated(invalidate, data)
        #     else:
        #         self.status += u" Adapter missing, can't invalidate Memcache."
