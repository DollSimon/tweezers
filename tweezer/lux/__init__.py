# coding=utf-8

__doc__ = """\
Re-implementation of the Optical Tweezer Toolbox in Python.

Tools for the computational modelling of optical tweezers.
"""

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]


from .dispersion import SellmeierCoefficients, dispersion
from .interfaces import (reflectance_s, reflectance_p, transmittance_p,
                         transmittance_s, Brewster_angle, angle_of_refraction)