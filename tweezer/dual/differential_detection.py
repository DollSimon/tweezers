# coding=utf-8
__doc__ = """\
Implements functions for differential detection procedure developed by Moffit et al.


Reference:
    1.	Differential detection of dual traps improves the spatial resolution of optical tweezers. 1–17, PNAS
"""

import numpy as np


def factors_for_optimal_coordinates(k1, r1, k2, r2, dist, kDNA, viscosity):
    """
    This function implements the differential detection, described by Moffitt et al., PNAS 2006.
    It returns the factors a1 and a2 for the optimal linear combination of the two bead deflections
    that minimises the noise. The factors are adjusted in a way, that one of them (a2) is 1 as the
    paper only gives an equation for the ratio a1 / a2.

    Args:
        xi   - bead deflection at trap i (in nm)
        jki   - trap stiffnesses (in pN / nm)
        ri   - bead radii (in nm)
        dist - distance from bead to bead (in nm)
        kDna - DNA stiffness (in pN / nm)
        viscosity  - well, the viscosity of the medium (in pN * s / nm^2)

    Returns:
        ai - factor for optimal linear combination of x1 and x2
    """
    g1 = 6 * np.pi * viscosity * r1
    g2 = 6 * np.pi * viscosity * r2

    G = 4 * np.pi * viscosity * dist


    a1 = g2 * (k1 + kDna) + g1 * kDna - g1 * g2 / G * (k1 + 2 * kDna)
    a2 = g1 * (k2 + kDna) + g2 * kDna - g1 * g2 / G * (k2 + 2 * kDna)

    # set a2 to 1 and get a1 based on that
    a1 = a1 / a2
    a2 = 1

    return a1, a2
