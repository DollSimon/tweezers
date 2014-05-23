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

DEPENDENCIES = ['pytest', 'docopt', 'pandas', 'tables', 'numpy',
                'scipy', 'termcolor', 'parsley', 'clint']

PACKAGES = ['tweezer',
            'tweezer.core',
            'tweezer.cli',
            'tweezer.scripts',
            'tweezer.bot',
            'tweezer.ixo',
            'tweezer.dia',
            'tweezer.simulate',
            'tweezer.noise',
            'tweezer.math',
            'tweezer.rnap',
            'tweezer.physics',
            'tweezer.polymer',
            'tweezer.statistics',
            'tweezer.single',
            'tweezer.dual']

MODULES = ['tweezer.io',
           # bot (TweeBot related) modules
           'tweezer.bot.utils',
           'tweezer.bot.configuration',
           # cli (command line interface) modules
           'tweezer.cli.help',
           'tweezer.cli.utils',
           'tweezer.cli.plots',
           # core modules
           'tweezer.core.polymer',
           'tweezer.core.dio',
           'tweezer.core.geometry',
           'tweezer.core.trap',
           'tweezer.core.watcher',
           'tweezer.constants',
           'tweezer.core.visualisation',
           'tweezer.core.simulations',
           'tweezer.core.trap_calibration',
           'tweezer.core.datatypes',
           'tweezer.core.analysis',
           'tweezer.core.parsers',
           'tweezer.core.overview',
           # dia (image processing related) modules
           'tweezer.dia.io',
           'tweezer.dia.tracking',
           'tweezer.dia.interactive',
           'tweezer.dia.utils',
           # dual (trap) modules
           'tweezer.dual.calibration',
           'tweezer.dual.theory',
           'tweezer.dual.differential_detection',
           # ixo (general utilities) module
           'tweezer.ixo.json_',
           'tweezer.ixo.decorators',
           'tweezer.ixo.git_',
           'tweezer.ixo.hdf5',
           'tweezer.ixo.pandas_',
           'tweezer.ixo.latex_',
           'tweezer.ixo.collections_',
           'tweezer.ixo.os_',
           'tweezer.ixo.r_',
           'tweezer.ixo.functions',
           'tweezer.ixo.math_',
           'tweezer.ixo.ipython_',
           # math modules
           'tweezer.math.geometry',
           # noise (fluctuations and signal processing) related modules
           'tweezer.noise.pwc',
           'tweezer.noise.filter',
           'tweezer.noise.ocl_filter',
           # physics (and chemistry and constants) modules
           'tweezer.physics.thermodynamics',
           'tweezer.physics.viscosity',
           'tweezer.physics.hydrodynamics',
           'tweezer.physics.electrostatics',
           'tweezer.physics.constants',
           # polymer (mainly dna) module
           'tweezer.polymer.dna',
           'tweezer.polymer.utils',
           # simulate (simulation related) modules
           'tweezer.simulate.brownian_motion',
           # single (trap) modules
           'tweezer.single.calibration',
           'tweezer.single.theory',
           'tweezer.single.utils',
           # statistics module
           'tweezer.statistics.wlc_models',
           # rnap (theory and models of transcription) modules
           'tweezer.rnap.pausing']

setup(
    name='tweezer',
    version=".".join(str(x) for x in __version__),
    description=DESCRIPTION,
    url='https://bitbucket.org/majahn/tweezer',
    author='Marcus Jahnel, MPI-CBG',
    author_email='jahnel@mpi-cbg.de',
    install_requires=DEPENDENCIES,
    packages=PACKAGES,
    package_data={'tweezer': ['data/*/*', 'templates/*/*', 'kernel/*/*',
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
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ),
)
