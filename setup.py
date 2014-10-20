#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

DESCRIPTION = ("Tools to read, analyse and interpret dual-trap\
 optical tweezer experiments")

LONG_DESCRIPTION = """
**tweezer** is an extensible Python package for the analysis\
 of dual-trap optical tweezer experiments.
"""

DEPENDENCIES = [# documentation stuff
                'sphinx',
                'sphinx_rtd_theme>=0.1',
                'sphinxcontrib-napoleon',
                'pytest',
                'pandas>=0.11',
                'numpy>=1.8',
                'matplotlib>=1.2.1',
                'ixo',
                'physics',
                'scipy',
                'seaborn'
]

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Natural Language :: English',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Topic :: Scientific/Engineering'
]

setup(
    name='tweezer',
    version='0.0.2',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://bitbucket.org/majahn/tweezer',
    author='Marcus Jahnel, MPI-CBG',
    author_email='jahnel@mpi-cbg.de',
    install_requires=DEPENDENCIES,
    packages=find_packages(),
    package_data={'tweezer': ['data/*/*',
                              'templates/*/*',
                              'kernel/*/*',
                              'data/settings/default_settings.json',
                              'data/settings/default.config.txt']},
    entry_points={
        'console_scripts': [
            'dt=tweezer.cli.main:start',
            'tweezer=tweezer.cli.main:start'
        ],
    },
    classifiers=CLASSIFIERS
)
