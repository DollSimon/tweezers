from __future__ import print_function, division

"""
Polymer
--------

A representation of semi-flexible polymers and \
corresponding classes.
"""
from collections import namedtuple

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt

from scipy.constants import Boltzmann
from numpy import sqrt

from clint.textui import colored, puts, indent 

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

        assert contour_length > 0
        assert persistence_length >0
        assert stretch_modulus >0
        assert temperature >0 

        self._S = np.float(stretch_modulus)
        self._P = np.float(persistence_length)
        self._L = np.float(contour_length)
        self._T = np.float(temperature)
        self._Boltzmann = Boltzmann
        self._kBT = self._T * self._Boltzmann * 1e21 # kBT in units of pN * nm
        self.units = {'P': 'nm', 'T': 'K', 'L': 'nm', 'S': 'pN', 'Boltzmann': 'J / K', 'kBT': 'pN nm'}

    @property
    def L(self):
        'Contour length of the polymer in the worm like chain model'
        return self._L
    
    @L.setter
    def L(self, value):
        if not isinstance(value, (int, float, np.float)):
            raise TypeError('Expect a number to set the contour length property')
        if value < 0:
            raise ValueError("Contour length is a positive quantity")

        self._L = np.float(value) 
    
    @L.deleter 
    def L(self):
        raise AttributeError("You can't delete the contour length property")
    
    @property
    def contour_length(self):
        'Contour length of the polymer in the worm like chain model'
        return self._L
    
    @contour_length.setter
    def contour_length(self, value):
        if not isinstance(value, (int, float, np.float)):
            raise TypeError('Expect a number to set the contour_length property')
        if value < 0:
            raise ValueError("Contour length is a positive quantity")

        self._L = np.float(value) 
    
    @contour_length.deleter 
    def contour_length(self):
        raise AttributeError("You can't delete the contour_length property")
    

    @property
    def stretch_modulus(self):
        'Stretch modulus of the worm-like chain model in pN'
        return self._S

    @stretch_modulus.setter 
    def stretch_modulus(self, value):
        if not isinstance(value, (int, float, np.float)):
            raise TypeError('Expect a number to set the stretch modulus')
        if value < 0:
            raise ValueError("Stretch modulus is a positive quantity")

        self._S = np.float(value)

    @stretch_modulus.deleter 
    def stretch_modulus(self):
        raise AttributeError("You can't delete the stretch modulus property")

    @property
    def S(self):
        'Stretch modulus of the worm-like chain model in pN'
        return self._S

    @S.setter 
    def S(self, value):
        if not isinstance(value, (int, float, np.float)):
            raise TypeError('Expect a number to set the stretch modulus, but got {}'.format(type(value)))
        if value < 0:
            raise ValueError("Stretch modulus is a positive quantity")

        self._S = np.float(value)

    @S.deleter 
    def S(self):
        raise AttributeError("You can't delete the stretch modulus property")
    
    @property
    def persistence_length(self):
        'Stretch modulus of the worm-like chain model in pN'
        return self._P

    @persistence_length.setter 
    def persistence_length(self, value):
        if not isinstance(value, (int, float, np.float)):
            raise TypeError('Expect a number to set the persistence length')
        if value < 0:
            raise ValueError("Persistence length is a positive quantity")

        self._P = np.float(value)

    @persistence_length.deleter 
    def persistence_length(self):
        raise AttributeError("You can't delete the persistence length property")

    @property
    def P(self):
        'Stretch modulus of the worm-like chain model in pN'
        return self._P

    @P.setter 
    def P(self, value):
        if not isinstance(value, (int, float, np.float)):
            raise TypeError('Expect a number to set the persistence length, but got {}'.format(type(value)))
        if value < 0:
            raise ValueError("Persistence length is a positive quantity")

        self._P = np.float(value)

    @P.deleter 
    def P(self):
        raise AttributeError("You can't delete the persistence length property")

    @property
    def T(self):
        'Temperature in K'
        return self._T
    
    @T.setter
    def T(self, value):
        if not isinstance(value, (int, float, np.float)):
            raise TypeError('Expect a number to set the temperature')
        self._T = np.float(value)
        self._kBT = self._T * self._Boltzmann * 1e21
    
    @T.deleter 
    def T(self):
        raise AttributeError("You can't delete the temperature")
    
    @property
    def thermal_energy(self):
        'Thermal energy in units of pN nm'
        return self._kBT

    @property
    def parameter(self):
        'Parameters for the worm like chain and their current values'
        parameters = namedtuple('Parameters', ['persistence_length', 'stretch_modulus'])
        return parameters(self._P, self._S)
    
    def extension(self, force, **kwargs):
        if not kwargs:
            contour_length = self._L
            persistence_length = self._P
            stretch_modulus = self._S
        else:
            contour_length = kwargs.get('L', self._L)
            persistence_length = kwargs.get('P', self._P)
            stretch_modulus = kwargs.get('S', self._S)
            
        f = np.float(force)

        if f >= 0:
            x = contour_length * (1 - (1 / 2.0) * sqrt((self._kBT) / (f * persistence_length)) +
                         (f / stretch_modulus))
        else:
            raise(ValueError("Force must be positive"))

        return x

    def __call__(self, force, **kwargs):
        return np.vectorize(self.extension)(force, **kwargs)

    def _repr_latex_(self):
        return r'$X_{\mathrm{eWLC}}(F\, ; L_{\mathrm{C}}\, , P\, , S\, ) = L_{\mathrm{C}}\big( 1 - \frac{1}{2}\sqrt{\frac{k_{\mathrm{B}} T}{P\,\cdot\, F}} + \frac{F}{S}\big)$'

    def formula(self):
        L = self._L
        P = self._P
        S = self._S
        return "X(F; L={L}, Lp={P}, S={S}) = L(1 - 1/2 * sqrt(kT/F*Lp) + F/S)".format(L=L, P=P, S=S)

    def diff_extension(self, force, **kwargs):
        """
        Returns the derivative of eWLC with respect to force
        """
        if not kwargs:
            contour_length = self._L
            persistence_length = self._P
            stretch_modulus = self._S
        else:
            contour_length = kwargs.get('L', self._L)
            persistence_length = kwargs.get('P', self._P)
            stretch_modulus = kwargs.get('S', self._S)
            
        f = np.float(force)

        if f >= 0:
            x = contour_length * ((1 / stretch_modulus) + (1 / 4.0) * (sqrt(self.kBT / persistence_length) * f**(-3.0/2)))
        else:
            raise(ValueError("Force must be positive"))

        return x

    def diff(self, force, **kwargs):
        return np.vectorize(self.diff_extension)(force, **kwargs)

    def stiffness(self, force, **kwargs):
        return 1.0/self.diff(force, **kwargs)

    def __repr__(self):
        L = self._L
        P = self._P
        S = self._S
        return "X(F; L={L}, Lp={P}, S={S}) = L(1 - 1/2 * sqrt(kT/F*Lp) + F/S)".format(L=L, P=P, S=S)

    def plot_example(self, force_range=[0.5, 50], **kwargs):
        force = np.linspace(min(force_range), max(force_range), 300)
        extension = self.__call__(force, **kwargs)
        with indent(2):
            puts('Plotting the {} with parameters:\n'.format(colored.green('extensible worm like chain model')))
        with indent(4):
            puts('Force range: {} - {} pN'.format(colored.yellow(min(force_range)), colored.yellow(max(force_range))))
            puts('Persistence length, P: {} nm'.format(colored.yellow(self._P)))
            puts('Stretch modulus, S: {} pN'.format(colored.yellow(self._S)))
            puts('Contour length, L: {} nm'.format(colored.yellow(self._L)))
        plt.plot(extension, force, color='#859900', linewidth=2.0, label='eWLC')
        plt.legend(loc=2)
        plt.xlabel('Extension [nm]')
        plt.ylabel('Force [pN]')
        plt.axvline(self._L, linewidth=1.0, linestyle='--', color='#d33682') 
        plt.show()
        return plt.gcf() 


class TwistedWormLikeChain(object):
    def __init__(self):
        raise NotImplementedError('Nope')


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
