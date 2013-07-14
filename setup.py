#!/usr/bin/env python

from setuptools import setup, find_packages 

setup(name='tscan',
  author='Sean Gallagher',
  author_email='stgallag@gmail.com',
  description='Command line image scanning swiss army knife',
  dependency_links = ["https://googledrive.com/host/0B8wOEC5-v5lXRVJ5Skl2d0VsTjQ/"],
  entry_points = {
    'console_scripts' : [ 'tscan = tscan.cli:call' ]
  },
  install_requires = ['numpy', 'futures', 'jsonpickle', 'mock'], # OpenCV isn't on PyPI
  license='GPLv3',
  packages=['tscan'],
  url='https://github.com/SeanTater/tscan',
  version='0.1a2',
 )
