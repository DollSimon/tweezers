from __future__ import print_function, division

import os
import glob

__all__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]

__doc__ = """\
Module that contains routines for noise analysis of time series 

One key aspect is to port the Steps and Bumps Toolkit from Matlab to Python 

Refs:

[1] M.A. Little, P.E. McSharry, S.J. Roberts, D.A.E. Costello, I.M.
Moroz (2007), Exploiting Nonlinear Recurrence and Fractal Scaling
Properties for Voice Disorder Detection, BioMedical Engineering OnLine
"""
