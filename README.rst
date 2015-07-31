=========
EEA Cache
=========
.. image:: http://ci.eionet.europa.eu/job/eea.cache-www/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.cache-www/lastBuild
.. image:: http://ci.eionet.europa.eu/job/eea.cache-plone4/badge/icon
  :target: http://ci.eionet.europa.eu/job/eea.cache-plone4/lastBuild

Introduction
============

This package combines the features from lovely.memcached and plone.memoize.ram.
It provides a decorator and utility for Memcaches at EEA.
The decorator allows you set dependencies known by eea.cache

.. note ::

  This add-on doesn't do anything by itself. It needs to be integrated by a
  developer within your own products. For reference you can check
  the `eea.app.visualization`_ package.

Contents
========

.. contents::

Main features
=============

1. Extends and overrides plone.memoize cache adapters to work with memcache
2. Provides an extended @cache decorator that supports:

   * cache lifetime override per method
   * dependencies string in order to bulk invalidate cache
   * auto-invalidation of cache when ObjectModifiedEvent is triggered

3. Possibility to manually invalidate cache via URL.

Install
=======

* Add eea.cache to your eggs and zcml section in your buildout and re-run buildout::

    eggs =
      ...
      eea.cache

    zcml =
      ...
      eea.cache
      eea.cache-overrides

* You can download a sample buildout from https://github.com/eea/eea.cache/tree/master/buildouts/plone4
* Install eea.cache within Site Setup > Add-ons
* Start memcache::

  $ bin/memcached start

Dependencies
============

* `python-memcached`_
* `pylibmc`_ (optional, for better performance)
* `plone.memoize`_
* `plone.uuid`_


Source code
===========

Latest source code (Zope 2 compatible):
  * `Plone Collective on Github <https://github.com/collective/eea.cache>`_
  * `EEA on Github <https://github.com/eea/eea.cache>`_


Cache decorator
===============

::

    >>> def key(method, self):
    ...     return method.__name__

    >>> from eea.cache import cache
    >>> @cache(key, dependencies=["frontpage"])
    ... def myMethod(num):
    ...     return num*num

Lets clear any running memcache::

    >>> from eea.cache.event import InvalidateMemCacheEvent
    >>> from zope.event import notify
    >>> notify(InvalidateMemCacheEvent(raw=True, dependencies=['frontpage']))

Our myMethod will now be cached with the key returned from the method 'key' and
with dependency 'frontpage'::

    >>> myMethod(2)
    4
    >>> myMethod(3)
    4

    >>> notify(InvalidateMemCacheEvent(raw=True, dependencies=['frontpage']))
    >>> myMethod(3)
    9

Cache lifetime
==============
By default your content is cached in memcache for one hour (3600 seconds). You
can change this by adding an **int** property within: ZMI > portal_properties >
site_properties called **memcached_defaultLifetime** and set it's value to
**86400** (one day) for example.


Cache lifetime override per key
-------------------------------

Starting with eea.cache 5.1 you can also pass a lifetime key with the duration
in seconds which will override the defaultLifetime either given from the
portal property or the default one from lovely.memcached of 3600 seconds::

    ex: in order to cache the result only for 4 minutes
    >>> @cache(key, dependencies=["frontpage"], lifetime=240)
    ... def myMethod(num):
    ...     return num*num


Invalidate cache
================
If you use cache decorator for BrowserView methods or directly on Zope objects
methods cache will be **automatically invalidated** when object is modified
(ObjectModifiedEvent is triggered)::

    >>> from Products.Five.browser import BrowserView

    >>> class XXX(BrowserView):
    ...     @cache(key)
    ...     def title(self):
    ...         return self.context.title_or_id()

You can disable auto invalidation by providing the auto_invalidate param to @cache
decorator::

    >>> @cache(key, auto_invalidate=False)
    ... def title(self):
    ...     return self.context.title_or_id()

memcache.invalidate
-------------------
In order to manually invalidate memcached cache per object this package
provides a browser view called **memcache.invalidate**.
It will invalidate all memcached methods associated with current object's UID::

    http://localhost:2020/Plone/front-page/memcache.invalidate

You can also manually invalidate related items and back references::

    http://localhost:2020/Plone/front-page/memcache.invalidate/relatedItems

    http://localhost:2020/Plone/front-page/memcache.invalidate/backRefs

By default this method can be called by users with these roles:

* Editor
* CommonEditor
* Owner
* Manager

varnish.invalidate
-------------------
In order to manually invalidate memcached cache per object this package
provides a browser view called **varnish.invalidate**.
It will invalidate all memcached methods associated with current object's UID::

    http://localhost:2020/Plone/front-page/varnish.invalidate

You can also manually invalidate related items and back references::

    http://localhost:2020/Plone/front-page/varnish.invalidate/relatedItems

    http://localhost:2020/Plone/front-page/varnish.invalidate/backRefs

By default this method can be called by users with these roles:

* Editor
* CommonEditor
* Owner
* Manager

cache.invalidate
----------------
In order to manually invalidate cache (memcached and varnish) per object this
package provides a browser view called **cache.invalidate**.
It will call memcache.invalidate and varnish.invalidate::

    http://localhost:2020/Plone/front-page/cache.invalidate

You can also manually invalidate related items and back references::

    http://localhost:2020/Plone/front-page/cache.invalidate/relatedItems

    http://localhost:2020/Plone/front-page/cache.invalidate/backRefs

By default this method can be called by users with these roles:

* Editor
* CommonEditor
* Owner
* Manager

cache.settings
--------------
There is also a Cache Tab per object where you can manually select which cache
to invalidate. By default, you can invalidate memcache and varnish. You also
have the possibility to invalidate memcache and/or varnish for related items
and also fo back references.

This form can be extended with more options. For a more detailed
example see `eea.pdf`_

**configure.zcml**::

  <adapter
    zcml:condition="installed eea.cache"
    factory=".behavior.ExtraBehavior"
    />

  <adapter
    zcml:condition="installed eea.cache"
    factory=".behavior.ExtraSettings"
    name="eea.pdf.cache.extender"
    />

**behavior.py**::

  # Model
  class IExtraSettings(model.Schema):
      """ Extra settings
      """
      pdf = schema.Bool(
          title=_(u"PDF"),
          description=_(u"Invalidate latest generated PDF file"),
          required=False,
          default=False
      )


  # Behaviour
  class ExtraBehavior(object):
      implements(IExtraSettings)
      adapts(IPDFAware)

      def __init__(self, context):
          self.context = context

      @property
      def pdf(self):
          """ PDF
          """
          return False

      @pdf.setter
      def pdf(self, value):
          """ Invalidate last generated PDF?
          """
          if not value:
              return

          removePdfFiles()

  # Form
  class ExtraSettings(extensible.FormExtender):
      adapts(IPDFAware, ILayer, SettingsForm)

      def __init__(self, context, request, form):
          self.context = context
          self.request = request
          self.form = form

      def update(self):
          """ Extend form
          """
          self.add(IExtraSettings, prefix="extra")
          self.move('pdf', after='varnish', prefix='extra')


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The eea.cache (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding and project management
==============================

EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
.. _`EEA Cache`: http://eea.github.com/docs/eea.cache
.. _`plone.recipe.zope2instance`: http://pypi.python.org/pypi/plone.recipe.zope2instance
.. _`eea.app.visualization`: http://eea.github.com/docs/eea.app.visualization
.. _`plone.memoize`: http://pypi.python.org/pypi/plone.memoize
.. _`pylibmc`: http://pypi.python.org/pypi/pylibmc
.. _`plone.uuid`: http://pypi.python.org/pypi/plone.uuid
.. _`python-memcached`: http://pypi.python.org/pypi/python-memcached
.. _`eea.pdf`: http://eea.github.io/docs/eea.pdf
