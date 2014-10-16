# coding=utf-8
from collections import namedtuple
from numpy import sqrt


SellmeierCoefficients = namedtuple('SellmeierCoefficients', ['B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'C4'])

SellmeierCoefficients.__doc__ = """\
Empirically determined coefficients used in the calculation of the dispersion \
properties of an transparent material. The first Sellmeier coefficients \
B1, B2, and B3, etc. are dimensionless. The next coefficients C1, C2, and C3 are usually \
reported in [µm^2].
"""


SELLMEIER_BK7 = SellmeierCoefficients(1.03961212, 0.231792344, 1.01046945, 0,
                                      6.00069867E-3, 2.00179144E-2, 1.03560653E2, 0)


def dispersion(wavelength = 1.064, SellmeierCoefficients = SELLMEIER_BK7, controlWavelength = True):
    """
    Dispersion formula based on the [Sellmeier equation]_

    How does the index of refraction of a material change with wavelength.

    Args:
        wavelength (float): Wavelength of light, λ, in [µm]. (Default: 1.064 µm)
        SellmeierCoefficients (namedtuple): Material specific coefficients for calculating dispersion
        controlWavelength (bool): Flag to infer correct wavelength units. (Default: True)

    .. note::
        The wavelength, λ, used here is the vacuum wavelength, not the wavelegth \
        inside the material, which is λ/n(λ).

    Returns:
        n (float): Index of refraction

    .. [Sellmeier equation] Wikipidea entry (http://en.wikipedia.org/wiki/Sellmeier_equation)
    """
    # check if wavelength is provided in nm
    if (wavelength > 100) and controlWavelength:
        print("Assuming that λ was provided in [nm]. Converting to µm")
        wavelength /= 1000
        print("λ is now: {} µm".format(wavelength))

    # dimensionless Sellmeier coefficients
    B1 = SellmeierCoefficients.B1
    B2 = SellmeierCoefficients.B2
    B3 = SellmeierCoefficients.B3

    # coefficients with dimension [µm^2]
    C1 = SellmeierCoefficients.C1
    C2 = SellmeierCoefficients.C2
    C3 = SellmeierCoefficients.C3

    λ = wavelength

    n = sqrt(1 + B1 * λ**2 / (λ**2 - C1) + B2 * λ**2 / (λ**2 - C2) + B3 * λ**2 / (λ**2 - C3))

    return n








