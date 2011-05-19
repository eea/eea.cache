""" EEA Cache Installer
"""
from setuptools import setup, find_packages
import os

NAME = 'eea.cache'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="Tools and config for memcache related caching",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone cache eea',
      author='Sasha Vincic, European Environment Agency (EEA)',
      author_email='webadmin@eea.europa.eu',
      url='http://svn.eionet.europa.eu/projects/'
          'Zope/browser/trunk/eea.cache',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['eea'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'lovely.memcached',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
