from scipy.constants import Boltzmann
import numpy as np

from tweezers.physics.thermodynamics import kbt


def extWlc(F, p=50, S=1000, L=1000, T=25):
    """
    Extensible worm-like chain model.

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


def dnaTwistStretchCoupling(F):
    """
    ref: Groß et al

    Args:
        F:

    Returns:

    """

    Fc = 30
    g0 = -637
    g1 = 17.9

    g = np.zeros_like(F)
    g[F < Fc] = -100
    g[F >= Fc] = g0 + g1 * F[F >= Fc]
    return g


def tWlc(F, p=50, S=1000, C=440, L=1000, T=25):

    g = dnaTwistStretchCoupling(F)
    # twistable worm-like chain
    d = L * (1 - 0.5 * np.sqrt(kbt(T) / (F * p)) + C * F / (-g**2 + S * C))
    return d
