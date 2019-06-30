from scipy.constants import Boltzmann
import numpy as np

from tweezers.physics.thermodynamics import kbt


def extWlc(F, p=50, S=1000, L=1000, T=25):
    """
    Extensible worm-like chain model.

    $x(F) = L * \left( 1 - \frac{1}{2} \sqrt{\frac{k_\mathrm{B}T}{F L_p}} + \frac{F}{S} \right)$

    Args:
        F: force [pN]
        p: persistence length [nm]
        S: stretch modulus [pN]
        L: contour length [nm]
        T: temperature [°C]

    Returns:
        extension [nm]
    """

    # extensible worm-like chain model

    # calculate distance
    d = L * (1 - 0.5 * np.sqrt(kbt(T) / (F * p)) + F / S)
    return d


def tWlc(F, p=50, S=1000, L=1000, g0=-637, g1=17.9, Fc=30, C=440, T=25):

    # units: g0: pn nm
    #        g1: nm
    #        C: pN nm^2

    # DNA twist-stretch coupling
    g = np.zeros_like(F)
    g[F < Fc] = g0 + g1 * Fc
    g[F >= Fc] = g0 + g1 * F[F >= Fc]

    # twistable worm-like chain
    d = L * (1 - 0.5 * np.sqrt(kbt(T) / (F * p)) + C * F / (-g**2 + S * C))
    return d


def fjc(F, b, S, L, T=25):
    """
    Extensible Freely jointed chain, see Smith et al 1996 (https://doi.org/10.1126%2Fscience.271.5250.795)

    $x(f) = L \left[ \coth\left(\frac{F b}{k_\mathrm{B}T}\right) - \frac{k_\mathrm{B}T}{F b} \right]  \left( 1 + \frac{F}{S} \right)$

    Args:
        F:
        b:
        S:
        L:
        T:

    Returns:

    """
    kt = kbt(T)
    fb = b * F
    # calculate extension
    d = L * (1 / np.tanh(fb / kt) - kt / fb) * (1 + F / S)
    return d
