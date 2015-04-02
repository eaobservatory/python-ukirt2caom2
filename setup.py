#!/usr/bin/env python

import os
from distutils.core import setup

setup(name='ukirt2caom2',
      version='0.1.0',
      author='Graham Bell',
      author_email='g.bell@jach.hawaii.edu',
      url='https://github.com/eaobservatory/python-ukirt2caom2',
      description='UKIRT 2 CAOM2',
      package_dir={'': 'lib'},
      packages=['ukirt2caom2'],
      scripts=[os.path.join('scripts', script) for script in [
                   'ukirt2caom2',
                   'ukirt_archive_submit',
              ]],
      requires=[
                'Sybase',
                'astropy',
                'caom2repoClient',
                'palpy',
                'pymongo',
                'taco',
                'tools4caom2',
               ],
     )
