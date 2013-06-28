#!/usr/bin/env python
#-*- coding: utf-8 -*-

import numpy as np


def calc_drag_on_sphere(radius=1000, viscosity=0.9e-9):
    """
    Calculates the simple Stokes' drag coefficient of a sphere in a Newtonian fluid
    
    :param radius: (number) radius of solid sphere in [nm]
    :param viscosity: (number) dynamic viscosity in [pN/nm^2 s] 

    :return drag_coefficent: description
    """
    if not isinstance(radius, (int, float, np.float)):
        try:
            radius = np.float(radius)
        except:
            print('Radius must be a number, not a {}'.format(type(radius)))

    if not isinstance(viscosity, (int, float, np.float)):
        try:
            viscosity = np.float(viscosity)
        except:
            print('Viscosity must be a number, not a {}'.format(type(viscosity)))
    
    assert (radius > 0), 'Radius of sphere must be positive'
    
    drag_coefficient = 6 * np.pi * radius * viscosity
    return drag_coefficient


class StokesDragSphere(object):
    def __init__(self):
        raise NotImplementedError('Nope')

class TwoSphereHydrodynamicInteractions(object):
    def __init__(self):
        raise NotImplementedError('Nope')


class TemperatureDependentViscosity(object):
    def __init__(self):
        raise NotImplementedError('Nope')

