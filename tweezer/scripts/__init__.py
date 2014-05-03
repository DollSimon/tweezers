from __future__ import print_function, division

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]

__doc__ = """\
Module that contains general scripts that can be invoked from command line.
"""
