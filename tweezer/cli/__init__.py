from __future__ import print_function, division

__modules__ = ['main', 'utils']

__doc__ = """\
Command line interface for the tweezer data analysis software
"""

import os
import glob

from collections import defaultdict

__all__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]

InterpretUserInput = defaultdict(list, yes=True, y=True, Y=True, ja=True, Yes=True,
    no=False, n=False, N=False, NO=False, nee=False)
