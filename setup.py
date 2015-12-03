#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

DESCRIPTION = ("Tools to read, analyse and interpret dual-trap\
 optical tweezers experiments")

LONG_DESCRIPTION = """
**tweezers** is an extensible Python package for the analysis\
 of dual-trap optical tweezers experiments.
"""

DEPENDENCIES = [# documentation stuff
                'sphinx',
                'sphinx_rtd_theme>=0.1',
                'pytest',
                'pandas>=0.15',
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
    name='tweezers',
    version='0.0.2',
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://bitbucket.org/majahn/tweezer',
    author='Marcus Jahnel, MPI-CBG',
    author_email='jahnel@mpi-cbg.de',
    install_requires=DEPENDENCIES,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'dt=tweezers.cli.main:start',
            'tweezers=tweezers.cli.main:start'
        ],
    },
    classifiers=CLASSIFIERS
)
