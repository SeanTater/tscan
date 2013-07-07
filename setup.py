#!/usr/bin/env python

from setuptools import setup, find_packages 

setup(name='tscan',
  author='Sean Gallagher',
  author_email='stgallag@gmail.com',
  description='Command line image scanning swiss army knife',
  entry_points = {
    'console_scripts' : [ 'tscan = tscan.caller:call' ]
  },
  install_requires = ['numpy'],#['cv2'],
  license='GPLv3',
  packages=find_packages(),
  url='https://github.com/SeanTater/tscan',
  version='0.1a2',
 )
