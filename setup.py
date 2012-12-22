#! /usr/bin/env python
from distutils.core import setup

DESCRIPTION = ("Tools to read, analyse and interpret dual-trap\
 optical tweezer experiments")

LONG_DESCRIPTION = """
**tweezer** is an extensible Python package for the analysis\
 of dual-trap optical tweezer experiments.

"""


config = {
    'description': DESCRIPTION,
    'long_description': LONG_DESCRIPTION,
    'author': 'Marcus Jahnel, MPI-CBG',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'jahnel@mpi-cbg.de',
    'version': '0.1',
    'install_requires': ['nose', 'pytest', 'pandas', 'tables',
    'scipy', 'numpy'],
    'packages': ['tweezer', 'tweezer.gui', 'tweezer.ott',
    'tweezer.core'],
    'py_modules': ['first_function', 'rocket', 'fio', 'sun', 'io', 'utils',
    'polymer', 'geometry', 'trap', 'simulations'],
    'scripts': [],
    'name': 'tweezer'
}

setup(**config)
