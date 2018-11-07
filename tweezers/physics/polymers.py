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

    # extensible wormlike chain model

    # calculate distance
    d = L * (1 - 0.5 * np.sqrt(kbt(T) / (F * p)) + F / S)
    return d
