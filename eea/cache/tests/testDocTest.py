""" Doctest
"""
import unittest
import doctest
from zope import component
from zope.component import provideUtility
from zope.testing.module import setUp, tearDown
from zope.configuration.xmlconfig import XMLConfig
from eea.cache.interfaces import IMemcachedClient
from eea.cache.tests.fake import FakeMemcachedClient
import eea.cache

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def eeaSetUp(test):
    """ Setup
    """
    setUp(test)
    XMLConfig('meta.zcml', component)()
    XMLConfig('overrides.zcml', eea.cache)()
    provideUtility(FakeMemcachedClient(), IMemcachedClient)

def test_suite():
    """ Test suite
    """
    level1Suites = (
        doctest.DocFileSuite('README.txt',
                             package='eea.cache',
                             optionflags=OPTIONFLAGS,
                             setUp=eeaSetUp,
                             tearDown=tearDown),
    )
    return unittest.TestSuite(level1Suites)
