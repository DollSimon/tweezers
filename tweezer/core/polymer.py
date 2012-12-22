"""
Polymer
--------

An abstraction representation of semi-flexible polymers and \
corresponding classes.
"""
from scipy.constants import Boltzmann
from math import sqrt
from numpy import nan


class ExtensibleWormLikeChain(object):
    """
    Extensible WLC Model according to Odijk, T. Stiff chains \
    and filaments under tension. Macromolecules (1995).

    X(F; L, Lp, S) = L(1 - 1/2*sqrt(kT/F*Lp) + F/S)

    Parameter:
        L - contour_length
        P - persistence_length (50 nm)
        S - stretch_modulus (1200 pN)
        T - temperature (295 K)

    Methods:
        constructor(L, P, S, T): set parameter (with default values)
        extension(force): compute the extension at a certain force
        formula(): print out formula used
    """

    def __init__(self, contour_length, persistence_length=50,
                 stretch_modulus=1200, temperature=295):

        self.S = float(stretch_modulus)
        self.P = float(persistence_length)
        self.L = float(contour_length)
        self.T = float(temperature)

    def __call__(self, force):
        kB = Boltzmann
        f = float(force)

        if f >= 0:
            x = self.L * (1 - (1 / 2.0) * sqrt((kB * self.T) / (f * self.P)) +
                         (f / self.S))
        else:
            x = nan

        return x

    def extension(self, force):
        kB = Boltzmann
        f = float(force)

        if f >= 0:
            x = self.L * (1 - (1 / 2.0) * sqrt((kB * self.T) / (f * self.P)) +
                         (f / self.S))
        else:
            x = nan

        return x

    def formula(self):
        return "X(F; L, Lp, S) = L(1 - 1/2 * sqrt(kT/F*Lp) + F/S)"


class LengthDependentPersistenceLength(object):
    """
    Implements the empirical length-dependent persistence length formula of:

    Ribezzi-Crivellari, M. & Ritort, F. \
    Force Spectroscopy with Dual-Trap Optical Tweezers:
    Molecular Stiffness Measurements and Coupled Fluctuations \
    Analysis. Biophys J (2012).

    `Paper Link <http://www.cell.com/biophysj/abstract/S0006-3495(12)01059-4>`_

    Parameter:
        L - contour_length of semiflexible polymer (unit: nm)
        P_inf - projected persistence length for infinitely long polymer
        a - configuration-dependent unit-less parameter

    """

    def __init__(self, persistence_length_infinity=50, a=4):
        self.P_inf = persistence_length_infinity
        self.a = a

    def __call__(self, contour_length):
        L = float(contour_length)

        P = self.P_inf / (1 + self.a * (self.P_inf / L))

        return P
