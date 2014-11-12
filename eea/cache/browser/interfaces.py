""" Browser interfaces

   >>> portal = layer['portal']
   >>> sandbox = portal['sandbox']

"""
from zope.interface import Interface
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
