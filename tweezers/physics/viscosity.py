#!/usr/bin/env python
#-*- coding: utf-8 -*-

__doc__ = """Calculate viscosity of water-glycerol mixtures according to \
[Cheng](http://www3.ntu.edu.sg/home/cnscheng/Publications/reprint/Glycerin-\
    water%20viscosity%20paper%20_sent%20to%20Ind%20Eng%20Chem%20Res.pdf)

The following variables are used:

Temperature T: [0, 100] in [C]
"""

from numpy import exp


def dynamicViscosityWaterGlycerol(waterVolume=1,
                                     glycerolVolume=0,
                                     temperature=25):
    """
    Power law equation for the dynamic viscosity of a water \
    to glycerol mixture according to:

    .. math:: \mu = \mu_{w}^{\alpha} \mu_{g}^{1 - \alpha}

    Args:
        waterVolume (float): volume of water in l
        glycerolVolume (float): volume of glycerol in l
        temperature (float): in Celsius in the range [0, 100]

    Returns:
        dynamic viscosity in [0.001 N s / m^2] (or cP)

    """

    # read input
    T = float(temperature)
    wV = float(waterVolume)
    gV = float(glycerolVolume)

    # get component viscosities
    mu_w = dynamicViscosityWater(temperature)
    mu_g = dynamicViscosityGlycerol(temperature)
    Cm = calcGlycerolFractionByMass(wV, gV, T)

    # compute coefficient required by Cheng formula
    a = 0.705 - 0.0017 * T
    b = (4.9 + 0.036 * T) * a ** 2.5
    alpha = 1 - Cm + (a * b * Cm * (1 - Cm)) / (a * Cm + b * (1 - Cm))

    # calculate viscosity
    mu = mu_w ** alpha * mu_g ** (1 - alpha)

    return mu


def dynamicViscosityWater(temperature=25):
    """
    Calculates :math:`\mu_w`, the dynamic viscosity of water, using the interpolation formula of Cheng.

    Args:
        temperature (float): in Celsius in the range [0, 100]

    Returns:
        :class:`float` Dynamic viscosity of water in [0.001 N s / m^2]
    """
    T = float(temperature)
    mu = 1.790 * exp(((-1230 - T) * T) / (36100 + 360 * T))
    waterDynamicViscosity = 0.001 * mu

    return waterDynamicViscosity


def dynamicViscosityGlycerol(temperature=25):
    """
    Calculates :math:`\mu_g`, the dynamic viscosity of glycerol, using the interpolation formula of Cheng.

    Args:
        temperature (float): in Celsius in the range [0, 100]

    Returns:
        :class:`float` Dynamic viscosity of glycerol in [0.001 N s / m^2]
    """
    T = float(temperature)
    mu = 12100 * exp(((-1233 + T) * T) / (9900 + 70 * T))
    glycerolDynamicViscosity = 0.001 * mu

    return glycerolDynamicViscosity


def densityWater(temperature):
    """
    Calculates the density of water from an interpolation by Cheng (see viscosity docstring for reference).

    Args:
        temperature (float): in Celsius in the range [0, 100]

    Returns:
        :class:`float` Density of water in kg/m^3
    """
    rho = 1000 * (1 - abs((temperature - 4) / (622.0)) ** (1.7))
    waterDensity = rho

    return waterDensity


def densityGlycerol(temperature):
    """
    Calculates the density of glycerol from an interpolation by Cheng (see viscosity docstring for reference).

    Args:
        temperature (float): in Celsius in the range [0, 100]

    Returns:
        :class:`float` Density of Glycerol in kg/m^3
    """
    rho = 1277 - 0.654 * temperature
    glycerolDensity = rho

    return glycerolDensity


def densityWaterGlycerol(waterVolume, glycerolVolume, temperature=25):
    """
    Calculates the density of a glycerol-water mixture from an interpolation by Cheng
    (see viscosity docstring for reference).

    Args:
        waterVolume (float): volume fraction of water (range is [0, 1])
        glycerolVolume (float): volume fraction of glycerol (range is [0, 1])
        temperature (float): in Celsius in the range [0, 100]

    Returns:
        :class:`float` density of the mixture in kg/m^3
    """
    T = float(temperature)
    rW = densityWater(temperature)
    rG = densityGlycerol(temperature)
    Cm = calcGlycerolFractionByMass(waterVolume, glycerolVolume, T)

    rho = rG * Cm + rW * (1 - Cm)

    return rho


def calcGlycerolFractionByVolume(waterVolume, glycerolVolume):
    """
    Calculates the volume fraction of glycerol in a water - glycerol mixture

    Args:
        waterVolume (float): volume of water in l
        glycerolVolume (float): volume of glycerol in l

    Returns:
        :class:`float` Fraction of glycerol by volume in [0, 1]
    """
    gV = float(glycerolVolume)
    gW = float(waterVolume)

    try:
        Cv = gV / (gW + gV)
    except ZeroDivisionError:
        Cv = 0.0

    volumeFractionGlycerol = Cv

    return volumeFractionGlycerol


def calcWaterFractionByVolume(waterVolume, glycerolVolume):
    """
    Calculates the volume fraction of water in a water - glycerol mixture

    Args:
        waterVolume (float): volume of water in l
        glycerolVolume (float): volume of glycerol in l

    Returns:
        :class:`float` Fraction of water by volume in [0, 1]
    """
    gV = float(glycerolVolume)
    wV = float(waterVolume)

    try:
        Cv = wV / (wV + gV)
    except ZeroDivisionError:
        Cv = 0.0

    volumeFractionWater = Cv

    return volumeFractionWater


def calcGlycerolFractionByMass(waterVolume, glycerolVolume, temperature):
    """
    Calculates the mass fraction of glycerol in a water - glycerol mixture

    Args:
        waterVolume (float): volume of water in l
        glycerolVolume (float): volume of glycerol in l
        temperature (float): in Celsius in the range [0, 100]

    Returns:
        :class:`float` Fraction of glycerol by mass in [0, 1]
    """
    T = float(temperature)
    wM = calcMass(waterVolume, densityWater(T))
    gM = calcMass(glycerolVolume, densityGlycerol(T))

    try:
        Cm = gM / (wM + gM)
    except ZeroDivisionError:
        Cm = 0.0

    massFractionGlycerol = Cm

    return massFractionGlycerol


def calcMass(volume, density):
    """
    Calculates the mass of a given volume from its density

    Args:
        volume (float): in m^3
        density (float): in kg/m^3

    Returns:
        :class:`float` mass in kg
    """
    mass = volume * density
    return mass
