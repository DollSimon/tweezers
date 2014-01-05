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
            'tweezer.scripts', 'tweezer.bot', 'tweezer.ixo', 'tweezer.dia',
            'tweezer.simulate', 'tweezer.noise', 'tweezer.geom']

MODULES = ['tweezer.io', 'tweezer.core.dio', 'tweezer.cli.help',
           'tweezer.core.polymer', 'tweezer.core.geometry',
           'tweezer.core.trap', 'tweezer.core.watcher',
           'tweezer.core.visualisation', 'tweezer.core.simulations',
           'tweezer.core.trap_calibration', 'tweezer.core.datatypes',
           'tweezer.core.analysis', 'tweezer.core.parsers',
           'tweezer.core.overview', 'tweezer.cli.utils', 'tweezer.cli.plots',
           'tweezer.ixo.json_', 'tweezer.ixo.decorators', 'tweezer.ixo.git_',
           'tweezer.ixo.hdf5', 'tweezer.ixo.pandas_', 'tweezer.ixo.latex_',
           'tweezer.ixo.collections_', 'tweezer.ixo.os_', 'tweezer.ixo.r_',
           'tweezer.ixo.functions', 'tweezer.ixo.math_', 'tweezer.bot.utils',
           'tweezer.bot.configuration', 'tweezer.dia.io',
           'tweezer.dia.tracking', 'tweezer.ixo.ipython_', 'tweezer.dia.utils',
           'tweezer.simulate.brownian_motion']

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
        'data/settings/default_settings.json',
        'data/settings/default.config.txt']},
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
