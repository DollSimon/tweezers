# coding=utf-8
from numpy import sin, cos, arcsin, sqrt, arctan2


__doc__ = """/
Methods for calculating reflection and refraction phenomena at interfaces /
between media with different refraction indices.
"""


def angle_of_refraction(n1 = 1.0, n2 = 1.33, θ1 = 0):
    """
    Angle of refraction according to the Snell's Law.

    n1 / n2 = sin(θ1) / sin(θ2)

    Args:
        n1 (float): Refractive index of medium 1.
        n2 (float): Refractive index of medium 2.
        θ1 (float): Angle of incidence in rad

    Returns:
        θ2 (float): angle of refraction
    """
    return arcsin((n1 / n2) * sin(θ1))


def reflectance_s(n1 = 1.0, n2 = 1.33, θi = 0):
    """
    Reflectance for s-polarized light according to the Fresnel formula.

    Reflectance, R, is defined as the fraction of the incident power that is /
    reflected from the interface.

    Args:
        n1 (float): Refractive index of medium 1.
        n2 (float): Refractive index of medium 2.
        θi (float): Angle of incidence in rad

    Returns:
        Rs (float): Reflectance of s-polarized light
        θr (float): Angle of reflection in rad
        θt (float): Angle of refraction (transmission) in rad
    """
    nominator = n1 * cos(θi) - n2 * sqrt(1 - (n1 / n2 * sin(θi))**2)
    denominator = n1 * cos(θi) + n2 * sqrt(1 - (n1 / n2 * sin(θi))**2)

    Rs = abs(nominator / denominator)**2
    θr = θi
    θt = angle_of_refraction(n1, n2, θi)

    return Rs, θr, θt


def reflectance_p(n1 = 1.0, n2 = 1.33, θi = 0):
    """
    Reflectance for p-polarized light according to the Fresnel formula.

    Reflectance, R, is defined as the fraction of the incident power that is /
    reflected from the interface.

    Args:
        n1 (float): Refractive index of medium 1.
        n2 (float): Refractive index of medium 2.
        θi (float): Angle of incidence in rad

    Returns:
        Rp (float): Reflectance of p-polarized light
        θr (float): Angle of reflection in rad
        θt (float): Angle of refraction (transmission) in rad
    """
    nominator = n1 * sqrt(1 - (n1 / n2 * sin(θi))**2) - n2 * cos(θi)
    denominator = n1 * sqrt(1 - (n1 / n2 * sin(θi))**2) + n2 * cos(θi)

    Rs = abs(nominator / denominator)**2
    θr = θi
    θt = angle_of_refraction(n1, n2, θi)

    return Rs, θr, θt


def transmittance_s(n1 = 1.0, n2 = 1.33, θi = 0):
    """
    Transmittance for s-polarized light according to the Fresnel formula.

    Transmittance, T, is defined as the fraction of the incident power that is /
    refracted through the interface.

    Args:
        n1 (float): Refractive index of medium 1.
        n2 (float): Refractive index of medium 2.
        θi (float): Angle of incidence in rad

    Returns:
        Ts (float): Transmittance of s-polarized light
        θr (float): Angle of reflection in rad
        θt (float): Angle of refraction (transmission) in rad
    """
    Rs = reflectance_s(n1, n2, θi)

    Ts = 1 - Rs
    θr = θi
    θt = angle_of_refraction(n1, n2, θi)

    return Ts, θr, θt


def transmittance_p(n1 = 1.0, n2 = 1.33, θi = 0):
    """
    Transmittance for p-polarized light according to the Fresnel formula.

    Transmittance, T, is defined as the fraction of the incident power that is /
    refracted through the interface.

    Args:
        n1 (float): Refractive index of medium 1.
        n2 (float): Refractive index of medium 2.
        θi (float): Angle of incidence in rad

    Returns:
        Tp (float): Transmittance of p-polarized light
        θr (float): Angle of reflection in rad
        θt (float): Angle of refraction (transmission) in rad
    """
    Rp = reflectance_p(n1, n2, θi)

    Tp = 1 - Rp
    θr = θi
    θt = angle_of_refraction(n1, n2, θi)

    return Tp, θr, θt


def Brewster_angle(n1, n2):
    """
    Brewster angle.
    """
    #TODO: check and add documentation.
    return arctan2(1, n1/n2)
