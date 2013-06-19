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
    'scipy', 'termcolor', 'parsley', 'clint']

PACKAGES = ['tweezer', 'tweezer.gui', 'tweezer.core', 'tweezer.cli', 
    'tweezer.ott', 'tweezer.scripts', 'tweezer.tweebot', 'tweezer.ixo']

MODULES = ['tweezer.io', 'tweezer.core.dio', 'tweezer.utils', 
    'tweezer.core.polymer', 'tweezer.core.geometry', 'tweezer.core.trap', 
    'tweezer.core.watcher', 'tweezer.core.visualisation', 
    'tweezer.core.simulations', 'tweezer.core.trap_calibration', 
    'tweezer.core.datatypes', 'tweezer.core.analysis', 'tweezer.core.parsers', 
    'tweezer.core.overview', 'tweezer.cli.utils', 'tweezer.tweebot.configuration',
    'tweezer.ixo.json', 'tweezer.ixo.decorators', 'tweezer.ixo.git', 
    'tweezer.ixo.hdf5', 'tweezer.ixo.latex', 'tweezer.ixo.os', 'tweezer.ixo.r',
    'tweezer.tweebot.utils'] 

setup(
    name='tweezer',
    version=".".join(str(x) for x in __version__),
    description=DESCRIPTION,
    url='https://bitbucket.org/majahn/tweezer',
    author='Marcus Jahnel, MPI-CBG',
    author_email='jahnel@mpi-cbg.de',
    install_requires=DEPENDENCIES,
    packages=PACKAGES,
    package_data={'tweezer': ['data/*/*', 'templates/*/*', 
        'data/settings/default_settings.json', 'data/settings/default.config.txt']},
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

