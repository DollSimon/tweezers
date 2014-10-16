# coding=utf-8
from tweezer.legacy.lux import dispersion

__doc__ = """\
Re-implementation of the Optical Tweezer Toolbox in Python.

Tools for the computational modelling of optical tweezers.
"""

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]


