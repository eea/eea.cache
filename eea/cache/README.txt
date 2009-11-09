=========
eea.cache
=========

This package combines the features from lovely.memcached and plone.memoize.ram.
It provides a decorator and utility for Memcaches at EEA.
The decorator allows you set dependencies known by lovely.memcached 

cache decorator
===============

  >>> def key(method, self):
  ...     return method.__name__


  >>> from eea.cache import cache
  >>> @cache(key, dependencies=u"frontpage")
  ... def myMethod(num):
  ...     return num*num
  
Our myMethod will now be cached with the key returned from the method 'key' and
with dependency 'frontpage'.

  >>> myMethod(2)
  4
  >>> myMethod(3)
  4


  >>> from lovely.memcached.event import InvalidateCacheEvent
  >>> from zope.event import notify
  >>> notify(InvalidateCacheEvent(raw=True, dependencies=[u'frontpage']))
  >>> myMethod(3)
  9

