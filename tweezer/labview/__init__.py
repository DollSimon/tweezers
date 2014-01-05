from __future__ import print_function, division

import os
import glob

__all__ = [os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__) + "/*.py")]

__doc__ = """\
Module that contains a prototype version of the Labview code

One aspect is to use Python for rapid prototyping and then port the code to LV
"""
