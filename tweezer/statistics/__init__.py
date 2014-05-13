__doc__ = """\
Module concerned with statistics and fitting of data.

Also concerns the parameter estimation with maximum likelihood methods.
"""

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]

# imports
from .wlc_models import fit_wlc
