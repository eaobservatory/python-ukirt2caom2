#!/usr/bin/env python

import os
from distutils.core import setup

setup(name='ukirt2caom2',
      version='0.1.0',
      author='Graham Bell',
      author_email='g.bell@jach.hawaii.edu',
      url='file:///home/gbell/git/ukirt2caom2.git',
      description='UKIRT 2 CAOM2',
      package_dir={'': 'lib'},
      packages=['ukirt2caom2'],
      #scripts=[os.path.join('scripts', script) for script in [
      #             'ukirt2caom2',
      #        ]],
      requires=[
                'Sybase',
                'astropy',
               ],
     )
