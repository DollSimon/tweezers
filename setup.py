#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

DESCRIPTION = ("Tools to read, analyse and interpret dual-trap\
 optical tweezers experiments")

LONG_DESCRIPTION = """
**tweezers** is an extensible Python package for the analysis\
 of dual-trap optical tweezers experiments.
"""

# todo: fix requirements, check which ones are actually required and in which version
DEPENDENCIES = [# documentation stuff
                'sphinx',
                'sphinx_rtd_theme >= 0.1',
                'pandas >= 0.19',
                'numpy >= 1.8',
                'matplotlib >= 1.2.1',
                'scipy',
                # when hdf5storage 0.2 is released on PyPi, this can be changed
                # 'hdf5storage >= 0.2',
                'hdf5storage @ https://github.com/frejanordsiek/hdf5storage/archive/master.zip',
                'jupyter',
                'npTDMS >= 0.11.4',
                'PyQt5',
                'pyinstaller'
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
