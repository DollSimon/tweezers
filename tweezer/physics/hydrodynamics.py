#!/usr/bin/env python
#-*- coding: utf-8 -*-

import numpy as np

from tweezer.physics import thermal_energy


def drag_sphere(radius=1000, dynamicViscosity=0.9e-9, verbose=False):
    """
    Calculates the simple Stokes' drag coefficient of a sphere in a Newtonian fluid
    at low Reynolds number.


    Parameters
    ----------
    radius : float
        Radius of solid sphere in [nm]
        Default: 1000 nm

    dynamicViscosity : float
        Dynamic viscosity in [pN/nm^2 s]
        Default: 0.9e-9 pN/nm^s s

    verbose : bool
        Print parameters and results with units
        Default: False

    Returns
    -------
    dragCoefficient : float
        Stokes drag coefficient in [pN/nm s]

    """
    if not isinstance(radius, (int, float, np.float)):
        try:
            radius = np.float(radius)
        except ValueError:
            print('Radius must be a number, not a {}'.format(type(radius)))

    if not isinstance(dynamicViscosity, (int, float, np.float)):
        try:
            dynamicViscosity = np.float(dynamicViscosity)
        except ValueError:
            print('Viscosity must be a number, not a {}'.format(type(dynamicViscosity)))

    assert (radius > 0), 'Radius of sphere must be positive'

    dragCoefficient = 6 * np.pi * radius * dynamicViscosity

    if verbose:
        print("In:")
        print("Radius: r = {} nm".format(radius))
        print("Viscosity: eta = {} pN/nm^2 s\n".format(dynamicViscosity))

        print("Out:")
        print("Drag coefficient: gamma = {} pN/nm s".format(round(dragCoefficient, 12)))

    return dragCoefficient


def diffusion_coefficient(radius=1000, temperature=25, dynamicViscosity=1e-9, verbose=False):
    """
    Calculates the diffusion coefficient for a sphere based on Stokes drag and the Stokes-Einstein relation.
    """
    kT = thermal_energy(temperature)
    drag = drag_sphere(radius=radius, dynamicViscosity=dynamicViscosity)



    return diffusionConstant



class StokesDragSphere(object):
    def __init__(self):
        raise NotImplementedError('Nope')

class TwoSphereHydrodynamicInteractions(object):
    def __init__(self):
        raise NotImplementedError('Nope')


class TemperatureDependentViscosity(object):
    def __init__(self):
        raise NotImplementedError('Nope')

