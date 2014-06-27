# coding=utf-8

__doc__ = """\
Pure math functions, especially geometric utilities.
"""

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]


from .geometry import Point, Vector, UnitVector, Line, Plane