=========
EEA Cache
=========

Introduction
============

This package combines the features from lovely.memcached and plone.memoize.ram.
It provides a decorator and utility for Memcaches at EEA.
The decorator allows you set dependencies known by lovely.memcached

.. note ::

  This add-on doesn't do anything by itself. It needs to be integrated by a
  developer within your own products. For reference you can check
  the `eea.app.visualization`_ package.

Contents
========

.. contents::


Installation
============

zc.buildout
-----------
If you are using `zc.buildout`_ and the `plone.recipe.zope2instance`_
recipe to manage your project, you can do this:

* Update your buildout.cfg file:

  * Add ``eea.cache`` to the list of eggs to install
  * Tell the `plone.recipe.zope2instance`_ recipe to install a ZCML slug
  * Add memcache

  ::

    parts +=
      libevent
      memcached
      memcached-ctl

    effective-user = zope-www

    [instance]
    ...
    eggs =
      ...
      eea.cache

    zcml =
      ...
      eea.cache-overrides


    [libevent]
    recipe = zc.recipe.cmmi
    url = http://www.monkey.org/~provos/libevent-1.4.8-stable.tar.gz

    [memcached]
    recipe = zc.recipe.cmmi
    url = http://www.danga.com/memcached/dist/memcached-1.2.6.tar.gz
    extra_options = --with-libevent=${libevent:location}

    [memcached-ctl]
    recipe = lovely.recipe:mkfile
    path = ${buildout:bin-directory}/memcached
    mode = 0755
    content =
     #!/bin/sh
     export LD_LIBRARY_PATH=${libevent:location}/lib

     PIDFILE=${memcached:location}/memcached.pid
        case "$1" in
          start)
           ${memcached:location}/bin/memcached -d -u ${buildout:effective-user} -P $PIDFILE
            ;;
          stop)
            kill `cat $PIDFILE`
            ;;
          restart|force-reload)
            $0 stop
            sleep 1
            $0 start
            ;;
          *)
            echo "Usage: $SCRIPTNAME {start|stop|restart}" >&2
            exit 1
            ;;
        esac

* Re-run buildout, e.g. with::

  $ bin/buildout -c buildout.cfg

* Restart memcache and Zope::

  $ bin/memcached restart
  $ bin/instance restart


Dependencies
============

`EEA Cache`_ has the following dependencies:
  - Plone 4+
  - lovely.memcached


Source code
===========

Latest source code (Zope 2 compatible):
  - `Plone Collective on Github <https://github.com/collective/eea.cache>`_
  - `EEA on Github <https://github.com/eea/eea.cache>`_


Cache decorator
===============

  >>> def key(method, self):
  ...     return method.__name__

  >>> from eea.cache import cache
  >>> @cache(key, dependencies=["frontpage"])
  ... def myMethod(num):
  ...     return num*num

Lets clear any running memcache

  >>> from lovely.memcached.event import InvalidateCacheEvent
  >>> from zope.event import notify
  >>> notify(InvalidateCacheEvent(raw=True, dependencies=['frontpage']))

Our myMethod will now be cached with the key returned from the method 'key' and
with dependency 'frontpage'.

  >>> myMethod(2)
  4
  >>> myMethod(3)
  4

  >>> notify(InvalidateCacheEvent(raw=True, dependencies=['frontpage']))
  >>> myMethod(3)
  4


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
