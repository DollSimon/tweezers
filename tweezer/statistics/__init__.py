# coding=utf-8
__doc__ = """\
OLS, MLE, Bayes and all that for fitting and learning from data

Parameter estimation with maximum likelihood methods.
"""

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]

# imports
from .wlc_models import fit_wlc
