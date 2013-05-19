__all__ = ['io', 'utils', 'ixo', 'ott', 'gui', 'core', 'scripts', 'cli']

__version__ = (0, 0, 1)

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))
def get_example_data(path):
    return os.path.join(_ROOT, 'data', path)

