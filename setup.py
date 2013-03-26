#!/usr/bin/env python
#-*- coding: utf-8 -*-

from tweezer import __version__

try:
    from setuptools import setup
except:
    from distutils.core import setup

DESCRIPTION = ("Tools to read, analyse and interpret dual-trap\
 optical tweezer experiments")

LONG_DESCRIPTION = """
**tweezer** is an extensible Python package for the analysis\
 of dual-trap optical tweezer experiments.
"""

DEPENDENCIES = ['nose', 'pytest', 'docopt', 'pandas', 'tables', 'numpy', 
    'scipy', 'termcolor']

PACKAGES = ['tweezer', 'tweezer.gui', 'tweezer.core', 'tweezer.cli', 
    'tweezer.ott', 'tweezer.scripts']

MODULES = ['dio', 'utils', 'polymer', 'geometry', 'trap', 'watcher', 
    'visualisation', 'simulations', 'trap_calibration', 'datatypes', 
    'analysis']

setup(
    name='tweezer',
    version=".".join(str(x) for x in __version__),
    description=DESCRIPTION,
    url='https://bitbucket.org/majahn/tweezer',
    author='Marcus Jahnel, MPI-CBG',
    author_email='jahnel@mpi-cbg.de',
    install_requires=DEPENDENCIES,
    packages=['tweezer', 'tweezer.gui', 'tweezer.cli', 'tweezer.ott', 'tweezer.'],
    entry_points={
        'console_scripts': [
            'dt=tweezer.cli.main:start',
            'tweezer=tweezer.cli.main:start'
        ],
    },
    py_modules=MODULES,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)

