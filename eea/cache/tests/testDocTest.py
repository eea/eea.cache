##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

import unittest
from zope import component
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite, DocFileSuite

from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds

from zope.app.testing import setup


def setUp(test):
    test.globs['root'] = setup.placefulSetUp(site=True)
    component.provideUtility(IntIds(), IIntIds)

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    level1Suites = (
        DocFileSuite(
            '../README.txt',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),
        )
    return unittest.TestSuite(level1Suites)


