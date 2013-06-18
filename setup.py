#!/usr/bin/env python
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup


classifiers = [
    'Development Status :: 4 - Beta'
  , 'Environment :: Console'
  , 'Environment :: Console :: Curses'
  , 'Intended Audience :: Developers'
  , 'License :: OSI Approved :: BSD License'
  , 'Natural Language :: English'
  , 'Operating System :: MacOS :: MacOS X'
  , 'Operating System :: Microsoft :: Windows'
  , 'Operating System :: POSIX'
  , 'Programming Language :: Python'
  , 'Topic :: Software Development :: Testing'
                ]

setup( name = 'assertEquals'
     , version = '0.4.3'
     , packages = [ 'assertEquals'
                  , 'assertEquals.cli'
                  , 'assertEquals.interactive'
                  , 'assertEquals.interactive.screens'
                  , 'assertEquals.tests'
                  , 'assertEquals.tests.interactive'
                   ]
     , entry_points = { 'console_scripts'
                      : [ 'assertEquals = assertEquals.cli.main:main' ]
                       }
     , description = 'assertEquals is an epic testing interface for Python.'
     , author = 'Chad Whitacre'
     , author_email = 'chad@zetaweb.com'
     , url = 'https://www.github.com/whit537/assertEquals/'
     , classifiers = classifiers
      )
