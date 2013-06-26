from __future__ import print_function, division

"""
Polymer
--------

A representation of semi-flexible polymers and \
corresponding classes.
"""
import numpy as np
import pandas as pd

from scipy.constants import Boltzmann
from math import sqrt



class ExtensibleWormLikeChain(object):
    """
    Extensible WLC Model according to Odijk, T. Stiff chains \
    and filaments under tension. Macromolecules (1995).

    X(F; L, Lp, S) = L(1 - 1/2*sqrt(kT/F*Lp) + F/S)

    Parameter:
    ----------
        L - contour_length
        P - persistence_length (50 nm)
        S - stretch_modulus (1200 pN)
        T - temperature (295 K)

    Methods:
    ---------
        constructor(L, P, S, T): set parameter (with default values)
        extension(force): compute the extension at a certain force
        formula(): print out formula used
    """

    def __init__(self, contour_length, persistence_length=50,
                 stretch_modulus=1200, temperature=295):

        self.S = np.float64(stretch_modulus)
        self.P = np.float64(persistence_length)
        self.L = np.float64(contour_length)
        self.T = np.float64(temperature)
        self.Boltzmann = Boltzmann
        self.kBT = self.T * self.Boltzmann * 1e21 # kBT in units of pN * nm
        self.units = {'P': 'nm', 'T': 'K', 'L': 'nm', 'S': 'pN', 'Boltzmann': 'J / K', 'kBT': 'pN nm'}

    def extension(self, force, **kwargs):
        if not kwargs:
            contour_length = self.L
            persistence_length = self.P
            stretch_modulus = self.S
        else:
            contour_length = kwargs.get('L', self.L)
            persistence_length = kwargs.get('P', self.P)
            stretch_modulus = kwargs.get('S', self.S)
            
        f = np.float64(force)

        if f >= 0:
            x = contour_length * (1 - (1 / 2.0) * sqrt((self.kBT) / (f * persistence_length)) +
                         (f / stretch_modulus))
        else:
            raise(ValueError("Force must be positive"))

        return x

    def __call__(self, force, **kwargs):
        return np.vectorize(self.extension)(force, **kwargs)

    def _repr_latex_(self):
        return r'$X_{\mathrm{eWLC}}(F\, ; L_{\mathrm{C}}\, , P\, , S\, ) = L_{\mathrm{C}}\big( 1 - \frac{1}{2}\sqrt{\frac{k_{\mathrm{B}} T}{P\,\cdot\, F}} + \frac{F}{S}\big)$'

    def formula(self):
        L = self.L
        P = self.P
        S = self.S
        return "X(F; L={L}, Lp={P}, S={S}) = L(1 - 1/2 * sqrt(kT/F*Lp) + F/S)".format(L=L, P=P, S=S)

    def __repr__(self):
        L = self.L
        P = self.P
        S = self.S
        return "X(F; L={L}, Lp={P}, S={S}) = L(1 - 1/2 * sqrt(kT/F*Lp) + F/S)".format(L=L, P=P, S=S)


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
