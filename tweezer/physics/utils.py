# coding=utf-8

import numpy as np


def as_Kelvin(temperatureInCelsius=25):
    """
    Converts temperature from Celsius to Kelvin

    Parameter
    ---------
    temperatureInCelsius : float
        Temperature in degree Celsius
        Default: 25 C

    Returns
    -------
    temperatureInKelvin : float
        Temperature in Kelvin
    """
    assert temperatureInCelsius >= -273.15

    temperatureInKelvin = 273.15 + temperatureInCelsius

    return temperatureInKelvin


def as_Celsius(temperatureInKelvin=298):
    """
    Converts temperature from Kelvin to Celsius

    Parameter
    ---------
    temperatureInKelvin : float
        Temperature in Kelvin
        Default: 298 K

    Returns
    -------
    temperatureInCelsius: float
        Temperature in degree Celsius
    """
    assert temperatureInKelvin >= 0

    temperatureInCelsius = temperatureInKelvin - 273.15

    return temperatureInCelsius


def volume_sphere(radius=1000):
    """
    Volume of a sphere

    Parameters
    ----------
    radius : float
        Radius in [nm]
        Default: 1000

    Returns
    -------
    volume : float
        Volume in [nm^3]
    """
    assert radius > 0

    volume = 4 / 3 * np.pi * radius**3

    return volume


def mass_sphere(radius=1000, density=1e-21, verbose=False):
    """
    Calculates mass of a sphere

    Parameters
    ----------
    radius : float
        Radius in [nm]
        Default: 1000

    density : float
        Density in [g / nm^3]

    Returns
    -------
    mass : float
        Mass in [g]
    """
    assert radius > 0
    assert density > 0

    volume = volume_sphere(radius = radius)

    mass = volume * density

    if verbose:
        print("Input:")
        print("Radius of Sphere [nm]: {}".format(radius))
        print("Density of material [g / nm^3]: {} \n".format(density))

        print("Output:")
        print("Mass of sphere [g]: {}\n".format(mass))

    return mass