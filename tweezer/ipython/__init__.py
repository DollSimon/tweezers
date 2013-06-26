from __future__ import print_function, division

__doc__ = """\
Module for ipython related utils
"""

import os
import glob

__all__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]
