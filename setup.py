try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Tweezer Project',
    'author': 'Marcus Jahnel, MPI-CBG',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it.',
    'author_email': 'jahnel@mpi-cbg.de',
    'version': '0.1',
    'install_requires': ['nose', 'py.test', 'pandas', 'tables'],
    'packages': ['tweezer'],
    'scripts': [],
    'name': 'tweezer_project'
}

setup(**config)
