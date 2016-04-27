import math
import numpy as np
from .hydrodynamics import dragSphere
from .thermodynamics import thermalEnergy
from .util import asKelvin

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

    beta = np.sqrt(thermalEnergy(asKelvin(T))/(dragSphere(radius, viscosity)*D))

    return beta
    

