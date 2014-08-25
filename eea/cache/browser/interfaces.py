""" Browser interfaces

   >>> portal = layer['portal']
   >>> sandbox = portal['sandbox']

"""
from zope.interface import Interface
from zope import schema
from eea.cache.config import EEAMessageFactory as _
try:
    from Products.statusmessages import interfaces
    IStatusMessage = interfaces.IStatusMessage
except ImportError:
    class IStatusMessage(Interface):
        """ Fallback interface
        """

try:
    from plone.app import caching
    VARNISH = caching
except ImportError:
    VARNISH = None

class ILayer(Interface):
    """ Custom browser layer for this package
    """



class ISettings(Interface):
    """ Cache settings
    """

    if VARNISH:
        varnish = schema.Bool(
            title=_(u"Varnish"),
            description=_(u"Also invalidate Varnish cache."),
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
