# coding=utf-8

import numpy as np
import pandas as pd


def angular_grid(nTheta:int=10, nPhi:int=10, output:int=0, inDegrees:bool=False):
    """
    Makes grid of points in theta and phi

    The default behaviour is to get numpy array of the points

    Parameters
    ----------
    nTheta: int
        Number of points for theta. Theta goes from 0 to pi.
        Default: 10

    nPhi: int
        Number of points for phi. Phi goes from 0 to 2 * pi.
        Default: 10

    output: int
        Output format of grid

        output  | description
        --------------------
        0       | Column vector
        1       | Matrix
        2       | Pandas Data Frame
        Default: 0 - column vector as numpy.array

    Returns
    -------
    grid : numpy.array
        Grid with equally distributed theta and phi angles.
    """
    theta = np.linspace(0, np.pi, nTheta)

    phi = np.linspace(0, 2 * np.pi, nPhi)

    if inDegrees:
        theta = [n * 180 / np.pi for n in theta]
        phi = [n * 180 / np.pi for n in phi]

    if output == 0:
        grid = np.array(theta + phi)
    elif output == 1:
        grid =

    return grid




