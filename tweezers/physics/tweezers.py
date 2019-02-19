import math
import numpy as np
from .hydrodynamics import dragSphere
from .thermodynamics import kbt
from .utils import asKelvin

def trapStiffness(fc=500, radius=1000, viscosity=8.93e-10):
    """
    Returns the trap stiffness (proposed units: [pN/nm])

    Args:
        fc (float): corner frequency in units of [Hz]
        radius (float): radius of the bead in units of [nm]
        viscosity (float): viscosity of the solution in units of [pN s /nm²]

    Returns:
        :class:`float`
    """

    kappa = 2*math.pi*fc*dragSphere(radius, viscosity)

    return kappa


def distanceCalibration(D=0.46, radius=1000, viscosity=8.93e-10, T=25):
    """
    Distance calibration factor (beta) in units of [nm/V]

    Args:
        D (float): diffusion constant in units of [V]
        radius (float): radius of the bead in units of [nm]
        viscosity (float): viscosity of the solution in units of [pN/nm^2s]
        T (float): temperature in units of [ºC]

    Returns:
        :class:`float`
    """

    beta = np.sqrt(kbt(T)/(dragSphere(radius, viscosity)*D))

    return beta


def lorentzian(f, D, fc):
    """
    Lorentzian function

    Args:
        f (:class:`numpy.array`): frequency in units of [Hz]
        D (`float`): diffusion constant in units of [V]
        fc (`float`): corner frequency in units of [Hz]

    Returns:
        :class:`numpy.array`
    """

    return D / (np.pi ** 2 * (f ** 2 + fc ** 2))


def tcOsciHydroCorrect(dist, rTrap=np.nan, rOther=np.nan, method='oseen'):
    """
    When using the oscillating calibration method with two beads, hydrodynamic interactions have to be taken into
    account. This function allows to calculate the correction factor using different methods.


    `oseen`: requires `dist` and `rOther`

    `rp` (Rotne Prager): requires `dist` and `rOther`

    `rpUneven` (Rotne Prager with spheres of different size): requires `dist`, `rTrap`, `rOther`

    Args:
        dist (float): distance between the traps (in nm)
        rTrap (float): radius of the bead in the trap for which to calculate the correction factor (in nm)
        rOther (float): radius of the bead in the other trap (in nm)
        method (str): currently only `oseen` is suppoted

    Returns:

    """

    if method == 'oseen':
        c = 1 - 1.5 * rOther / dist
    elif method == 'rp':
        c = 1 - 1.5 * rOther / dist + (rOther / dist)**3
    elif method == 'rpUneven':
        c = 1 - 1.5 * rOther / dist + 0.5 * rOther * (rTrap**2 + rOther**2) / dist**3
    else:
        raise ValueError('tcOsciHydroCorrect: "{}" moethod is not supported'.format(method))
    return c
