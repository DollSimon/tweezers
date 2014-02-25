#!/usr/bin/env python
#-*- coding: utf-8 -*-

from clint.textui import colored, puts

from tweezer.ixo.viscosity import calc_dynamic_viscosity_of_mixture


def calc_example(clean=False, *args, **kwargs):
    """
    This is an example calculation
    """
    def example(n=4, m=6, l=65):
        return n * m - l

    try:
        result = example()
        if clean:
            print(result)
        else:
            puts('Calculating example\n')
            puts('Result: {}'.format(result))

        return result
    except (KeyboardInterrupt, SystemExit), err:
        raise err


def calc_viscosity(clean=False, *args, **kwargs):
    """
    Command line interface to calculate the dynamic viscosity of water-glycerol
    mixtures.
    """
    try:
        result = calc_dynamic_viscosity_of_mixture(1, 2)
        funcArgs = None
        if clean:
            print(result)
        else:
            dynamicViscosity = round(result, 6)
            puts('Calculating the dynamic viscosity of Water-Glycerol mixture')
            puts('Dynamic viscosity: {} {}'.format(colored.red(dynamicViscosity),
                                                   'N s / m^2'))
        return result, funcArgs
    except (KeyboardInterrupt, SystemExit), err:
        raise err
