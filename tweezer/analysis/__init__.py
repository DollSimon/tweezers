# coding=utf-8
"""
Mixed routines for the middle steps of data analysis.
"""

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]

# imports
from .utils import (set_up_directories, is_trial_complete)
