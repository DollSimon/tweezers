from __future__ import print_function, division

__modules__ = ['polymer', 'geometry', 'trap', 'simulations', 'trap_calibration',
    'datatypes', 'analysis', 'watcher', 'visualisation', 'parsers', 'overview']

__doc__ = """\
Contains core modules and classes for analysing tweezer experiments.
"""

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]
