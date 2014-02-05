#!/usr/bin/env python

from distutils.core import setup
from distutils import sysconfig
from os.path import join as pjoin, split as psplit
from glob import glob
import sys
import platform

# Version number
major = 1
minor = 3
maintenance = 0

setup(name = "fenicstools",
      version = "%d.%d.%d" % (major, minor, maintenance),
      description = "fenicstools -- tools for postprocessing in FEniCS programs",
      author = "Mikael Mortensen",
      author_email = "mikaem@math.uio.no",
      url = 'https://github.com/mikaem/fenicstools.git',
      classifiers = [
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Programming Language :: Python :: 2.6',
          'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
          'Topic :: Scientific/Engineering :: Mathematics',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      packages = ["fenicstools",
                  # Note: These are not python packages because they only have C++ code:
                  #"fenicstools.fem",
                  #"fenicstools.Probe",
                  ],
      package_dir = {"fenicstools": "fenicstools"},
      package_data = {"fenicstools": ["Probe/*.h",
                                      "Probe/*.cpp",
                                      "fem/*.cpp"]},
    )

