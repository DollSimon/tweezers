from __future__ import print_function, division

__doc__ = """\
Geometry module with useful classes and functions.
"""

import os
import glob

MEMBER_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")

__all__ = [os.path.basename(f)[:-3] for f in MEMBER_FILES]
