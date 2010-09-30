from setuptools import setup, find_packages
import os
from os.path import join

name = 'eea.cache'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

setup(name=name,
      version=version,
      description="Tools and config for memcache related caching",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone cache eea',
      author='Sasha Vincic',
      author_email='sasha dot vincic at valentinewebsystems dot com',
      url='https://svn.eionet.europa.eu/projects/Zope/browser/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
