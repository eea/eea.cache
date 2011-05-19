""" Doctest
"""
import unittest
from zope.app  import component
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.component import provideUtility
from zope.app.testing.placelesssetup import setUp, tearDown
from zope.configuration.xmlconfig import XMLConfig
from lovely.memcached.interfaces import IMemcachedClient
from eea.cache.tests.fake import FakeMemcachedClient
import eea.cache

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def eeaSetUp(test):
    """ Setup
    """
    setUp()
    XMLConfig('meta.zcml', component)()
    XMLConfig('overrides.zcml', eea.cache)()
    provideUtility(FakeMemcachedClient(), IMemcachedClient)

def test_suite():
    """ Test suite
    """
    level1Suites = (
        DocFileSuite('README.txt',
                     package='eea.cache',
                     optionflags=OPTIONFLAGS,
                     setUp=eeaSetUp,tearDown=tearDown), )
    return unittest.TestSuite(level1Suites)
