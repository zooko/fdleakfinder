#!/usr/bin/env python

# fdleakfinder
#
# Author: Zooko Wilcox-O'Hearn
#
# See README.rst for licensing information.

import os

from setuptools import find_packages, setup

PKG='fdleakfinder'
VERSIONFILE = os.path.join(PKG, "_version.py")

import versioneer
versioneer.versionfile_source = VERSIONFILE
versioneer.versionfile_build = VERSIONFILE
versioneer.tag_prefix = "fdleakfinder-"
versioneer.parentdir_prefix = 'fdleakfinder'

trove_classifiers=[
    "Development Status :: 4 - Beta",
    "License :: OSI Approved",
    "License :: DFSG approved",
    "Intended Audience :: Developers",
    "Operating System :: Unix",
    "Natural Language :: English",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.7",
    "Topic :: Utilities",
    ]

data_fnames=[ 'COPYING.SPL.txt', 'README.rst',]

# In case we are building for a .deb with stdeb's sdist_dsc command, we put the
# docs in "share/doc/python-$PKG".
doc_loc = "share/doc/" + PKG
data_files = [(doc_loc, data_fnames)]

readmetext = open('README.rst').read()
if readmetext[:3] == '\xef\xbb\xbf':
    # utf-8 "BOM"
    readmetext = readmetext[3:].decode('utf-8')

setup(name=PKG,
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description='helps you figure out why your unix process uses too many file descriptors',
      long_description=readmetext,
      author="Zooko Wilcox-O'Hearn",
      author_email='zooko@zooko.com',
      url='https://github.com/zooko/' + PKG,
      license='BSD', # see README.rst for details
      packages=find_packages(),
      include_package_data=True,
      data_files=data_files,
      classifiers=trove_classifiers,
      entry_points = {
          'console_scripts': [
              'fdleakfinder = fdleakfinder.fdleakfinder:main',
              ] },
      test_suite=PKG+".test",
      zip_safe=False, # I prefer unzipped for easier access.
      install_requires=['pyutil'],
      )
