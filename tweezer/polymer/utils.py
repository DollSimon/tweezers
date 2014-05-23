# coding=utf-8
__doc__ = """\
Utilities for Polymer / DNA module
"""
import numpy as np


@np.vectorize
def as_nm(basePairs=1000, conversionFactor=0.338, verbose=False):
    """
    Convert base pairs (bp) or nucleotides (nt) into nanometers

    Args:
        basePairs (number or list of numbers): base pairs or nucleotides
        conversionFactor (float): crystallographic distance of base pair in dsDNA (optional, default 0.338)

    Returns:
        distanceInNm (float): corresponding distance in base pairs

    Example:
        >>> as_nm()
        >>> 338.0
    """
    distanceInNm = conversionFactor * basePairs

    if verbose:
        print(basePairs, "bp of dsDNA correspond to", distanceInNm, "nm.\n")

    return distanceInNm


@np.vectorize
def as_bp(distanceInNm=1000, conversionFactor=0.338, verbose=False):
    """
    Convert nano meters to base pairs (bp) or nucleotides (nt) to distance in [nm]

    Args:
        distanceInNm (number or list of numbers): distance(s) to be converted in [nm]
        conversionFactor (float): crystallographic distance of base pair in dsDNA, (default 0.338)

    Returns:
        basePairs (float or array of floats): number of base pairs corresponding to the distance
    """
    basePairs = distanceInNm / conversionFactor

    if verbose:
        print(distanceInNm, "nm correspond to", basePairs, "bp of dsDNA.\n")

    return basePairs
