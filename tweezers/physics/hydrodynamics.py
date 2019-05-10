import numpy as np
from .thermodynamics import kbt
from .utils import asKelvin


def dragSphere(radius=1000, viscosity=0.9e-9):
    """
    Calculates the simple Stokes' drag coefficient of a sphere in a Newtonian fluid
    at low Reynolds number. :math:`\\gamma = 6 \\pi \\eta r`

    Args:
        radius (float): radius of solid sphere (default: 1000 nm)
        viscosity (float): dynamic viscosity (default: 0.9e-9 pN s / nm²)

    Returns:
        :class:`float` Stokes drag coefficient in [pN/nm s]
    """

    dragCoefficient = 6 * np.pi * radius * viscosity

    return dragCoefficient


def diffusionCoefficient(radius=1000, temperature=25, viscosity=1e-9, verbose=False):
    """
    Calculates the diffusion coefficient for a sphere based on Stokes drag and the Stokes-Einstein relation.
    :math:`D = \\frac{kT}{\\gamma}`

    Args:
        radius (float): Radius of sphere in [nm] (Default: 1000 nm)
        temperature (float): Solvent temperature in °C (Default: 25)
        viscosity (float): Dynamic viscosity in [pN/nm^2 s] (Default: 0.9e-9 pN/nm^2 s)
        verbose (bool): Print parameters and results with units (Default: False)

    Returns:
        :class:`float` Diffusion constant in [nm^2 / s]
    """

    assert radius > 0
    assert temperature >= -273.15
    assert viscosity > 0

    kT = kbt(temperature)
    drag = dragSphere(radius=radius, viscosity=viscosity)

    diffusionConstant = kT / drag

    if verbose:
        print("In:")
        print("Radius: r = {} nm".format(radius))
        print("Temperature: T = {} °C".format(temperature))
        print("Dynamic viscosity: eta = {} pN/nm^2 s\n".format(viscosity))

        print("Out:")
        print("Diffusion constant: D = {} nm^2 / s".format(round(diffusionConstant, 12)))

    return diffusionConstant


def viscosityWater(T, absoluteT=False):
    """
    Calculate the viscosity of water at a given temperature from an `empiric equation`_ at Wikipedia in [pN s / nm^2].

    Args:
        T (float): Temperature
        absoluteT (bool): if `False`, temperature is given in [C], if `True` in [K]

    Returns:
        :class:`float` in [pN s / nm^2]

    .. _`empiric equation`:
        https://en.wikipedia.org/wiki/Temperature_dependence_of_liquid_viscosity#Viscosity_of_water
    """

    # formula empiric parameters
    A = 2.414E-5
    B = 247.8
    C = 140

    # get absolute temp
    if absoluteT:
        absT = T
    else:
        absT = asKelvin(T)

    # calculate viscosity and convert units
    n = A * 10**(B / (absT - C)) * 1E-6

    return n
