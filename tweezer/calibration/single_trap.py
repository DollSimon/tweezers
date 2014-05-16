__doc__ = """\
Thermal calibration of single optical trap.
"""

import numpy as np


def corner_frequency(dragCoefficient=2e-5, trapStiffness=0.1, verbose=False):
    """
    Corner frequency of the spectrum of a single trap.

    Parameters
    ----------
    dragCoefficient : float
        Stokes drag coefficient in [pN/nm s]
        Default: 2e-5 pN/nm s

    trapStiffness : float
        Trap stiffness in [pN/nm]
        Default: 0.1 pN/nm

    Returns
    -------
    cornerFrequency : float
        Characteristic frequency of the power spectrum in [Hz]

    """
    cornerFrequency = 2 * np.pi * trapStiffness / dragCoefficient

    if verbose:
        print("In:")
        print("Drag coefficient: gamma = {} pN/nm s".format(round(dragCoefficient, 12)))
        print("Trap stiffness: k = {} pN/nm^2 s\n".format(trapStiffness))

        print("Out:")
        print("Corner frequency: fc = {} Hz".format(cornerFrequency))

    return cornerFrequency


def detector_sensitivity(diffusionConstant=2, dragCoefficient=2e-5):
    pass