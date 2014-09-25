""" Browser
"""
from zope.component import queryAdapter, queryMultiAdapter
from zope.formlib.form import EditForm
from zope.formlib.form import Fields
from zope.formlib.form import action, setUpWidgets
from eea.cache.browser.interfaces import IStatusMessage
from eea.cache.browser.interfaces import ISettings
from eea.cache.config import EEAMessageFactory as _

class Settings(EditForm):
    """ Cache settings
    """
    label = _(u"Invalidate context related cache")
    form_fields = Fields(ISettings)

    def setUpWidgets(self, ignore_request=False):
        """ Sets up widgets
        """
        self.adapters = {}
        self._data = {}
        self.widgets = setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            form=self, data=self._data, adapters=self.adapters,
            ignore_request=ignore_request)

    @action(_(u'Invalidate'))
    def invalidate(self, saction, data):
        """ Invalidate cache
        """
        if data.get('varnish', False):
            invalidate = queryMultiAdapter((self.context, self.request),
                                           name='varnish.invalidate')
            if not invalidate:
                self.message = u"Adapter missing, can't invalidate Varnish."

        if data.get('memcache', False):
            invalidate = queryMultiAdapter((self.context, self.request),
                                           name='memcache.invalidate')
            if not invalidate:
                self.message = u"Adapter missing, can't invalidate Memcache."

        if not invalidate:
            return self.nextUrl

        self.message = invalidate()
        if data.get('relatedItems', False):
            invalidate.relatedItems()

        if data.get('backRefs', False):
            invalidate.backRefs()

        return self.nextUrl

    @property
    def nextUrl(self):
        """ Redirect to the default view
        """
        status = queryAdapter(self.request, IStatusMessage)
        if status:
            status.addStatusMessage(self.message, type='info')
        self.request.response.redirect(self.context.absolute_url())
