""" Subtyping interfaces
"""
from zope.interface import Interface

class ICacheAware(Interface):
    """ Marker interface for objects that are aware of eea.cache
    """
