# coding=utf-8

from tweezer.physics import thermal_energy
import matplotlib.pyplot as plt
import numpy as np

from IPython.html.widgets import interact


def explore_simple_wlc_model():
    """
    Construct widget to explore the worm-like chain model.

    .. note ::

        This function only works in the IPython notebook, but there it works beautifully...

    """
    #TODO: This is just a test. Get the real calculation from the correct polymer module
    def wlc(L, P, S):
        forces = np.linspace(1, 30)
        extensions = L * (1 - 1/4 * np.sqrt(thermal_energy() / (P * forces)) + forces / S)
        plt.plot(extensions, forces)
        plt.show()

    interact(wlc, L = (200.0, 300.0), P = (40.0, 60.0), S = (1000, 1500))
