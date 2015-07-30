=========
EEA Cache
=========
This package combines the features from lovely.memcached and plone.memoize.ram.
It provides a decorator and utility for Memcaches at EEA.
The decorator allows you set dependencies known by lovely.memcached.
It supports python-memcached and also libmemcached, through the pylibmc wrapper.

.. contents::

Usage
=====

.. note ::

  This add-on doesn't do anything by itself. It needs to be integrated by a
  developer within your own products. For reference you can check
  the `eea.app.visualization`_ package.

Cache decorator
===============

  >>> def key(method, self):
  ...     return method.__name__

  >>> from eea.cache import cache
  >>> @cache(key, dependencies=["frontpage"])
  ... def myMethod(num):
  ...     return num*num

Lets clear any running memcache

  >>> from eea.cache.event import InvalidateMemCacheEvent
  >>> from zope.event import notify
  >>> notify(InvalidateMemCacheEvent(raw=True, dependencies=['frontpage']))

Our myMethod will now be cached with the key returned from the method 'key' and
with dependency 'frontpage'.

  >>> myMethod(2)
  4
  >>> myMethod(3)
  4

  >>> notify(InvalidateMemCacheEvent(raw=True, dependencies=['frontpage']))
  >>> myMethod(3)
  4


Authors
=======

  EEA_ - European Environment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
.. _`eea.app.visualization`: http://eea.github.com/docs/eea.app.visualization
