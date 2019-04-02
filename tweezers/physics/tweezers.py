import math
import numpy as np
from .hydrodynamics import dragSphere
from .thermodynamics import kbt


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


def lorentzian(f, fc, D):
    """
    Lorentzian function

    Args:
        f (:class:`numpy.array`): frequency in units of [Hz]
        fc (`float`): corner frequency in units of [Hz]
        D (`float`): diffusion constant in units of [V]

    Returns:
        :class:`numpy.array`
    """

    return D / (np.pi ** 2 * (f ** 2 + fc ** 2))


def psdDiode(f, fc, D, fd3, a):
    """
    Functional form of the power spectral density (PSD) of a trap when taking into account diode effects (transparency
    of silicon at infrared). See `Berg-Sørensen et al.`_: "Power spectrum analysis for optical tweezers". They describe
    this effect as a low-pass filter.

    Args:
        f (`float`): frequency for which to evaluate the PSD value
        fc (`float`): corner frequency of the trap
        D (`float`): diffusion coefficient of the particle in the trap
        fd3 (`float`): roll-off frequency, f_(3 dB), of the diode
        a (`float`): constant describing the instantaneous fraction of the response

    Returns:
        `float`

    .. _Berg-Sørensen et al.:
        https://doi.org/10.1063/1.1645654
    """

    diode = (a ** 2 + (1 - a ** 2) / (1 + ((f / fd3) ** 2)))
    return diode * lorentzian(f, fc, D)


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
