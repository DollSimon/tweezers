# coding=utf-8
from collections import namedtuple

import numpy as np
import pandas as pd

from tweezer.physics import drag_sphere, mass_sphere

__doc__ = """\
Simulation of optical trap time series according to Norrelykke et al.
"""


def eigenvalues(dragCoefficient=drag_sphere(1000),
                massSphere=mass_sphere(1000),
                trapStiffness=0.1):
    """
    Calculates eigenvalues in the simulation of OTs according to Norrelykke et al.

    Parameters
    ----------
    dragCoefficient : float
        Drag

    massSphere : float
        Mass in [g / ]

    trapStiffness : float
        Stiffness in [pN / nm]
    """
    g = dragCoefficient
    m = massSphere
    k = trapStiffness

    discriminant = (g**2 / (4 * m**2)) - k / m

    prefactor = g / (2 * m)

    plus = prefactor + np.sqrt(discriminant)
    minus = prefactor - np.sqrt(discriminant)

    Eigenvalues = namedtuple("Eigenvalues", ['plus', 'minus'])

    eigenvalues = Eigenvalues(plus, minus)

    return eigenvalues


def cValues(eigenvalues=eigenvalues(), timeStep = 0.001):
    """
    Calculates c values in the simulation of OTs according to Norrelykke et al.

    Computes: c = exp(-λ * ∆t)

    Parameters
    ----------
    eigenvalues : namedtuple
        Eigenvalues of Langevin equation; namedtuple with "plus" and "minus" fields

    timeStep : float
        Difference between two time points; delta time
        Default: 0.001
    """
    cValues = namedtuple("cValues", ['plus', 'minus'])

    plus = np.exp(-eigenvalues.plus * timeStep)
    minus = np.exp(-eigenvalues.minus * timeStep)

    c = cValues(plus, minus)

    return c


def aValues(dragCoefficient=drag_sphere(1000), eigenvalues=eigenvalues(), cValues=cValues()):
    """
    Calculates A values in the simulation of OTs according to Norrelykke et al.
    """

    l = eigenvalues
    c = cValues
    D = dragCoefficient

    factorA = (l.plus + l.minus) / (l.plus - l.minus)
    factorB = np.sqrt((1 - c.plus**2) * D / (2 * l.plus))
    factorC = np.sqrt((1 - c.minus**2) * D / (2 * l.minus))

    aValues = namedtuple("aValues", ['plus', 'minus'])

    plus = factorA * factorB
    minus = factorA * factorC

    A = aValues(plus, minus)

    return A


def alpha(eigenvalues=eigenvalues(), cValues=cValues()):
    """
    Calculates alpha in the simulation of OTs according to Norrelykke et al.
    """
    l = eigenvalues
    c = cValues

    factorA = 2 * np.sqrt(l.plus * l.minus) / (l.plus + l.minus)
    factorB = (1 - c.plus * c.minus) / np.sqrt((1 - c.plus**2) * (1 - c.minus**2))

    alphaValue = factorA * factorB

    return alphaValue


def exp_Matrix(eigenvalues=eigenvalues(), cValues=cValues()):
    """
    Calculates alpha in the simulation of OTs according to Norrelykke et al.

    Computes: exp(-M * ∆t)
    """
    l = eigenvalues
    c = cValues

    prefactor = 1 / (l.plus - l.minus)

    M = np.matrix(np.zeros((2, 2)))

    M[0, 0] = -l.minus * c.plus + l.plus * c.minus
    M[0, 1] = -c.plus + c.minus
    M[1, 0] = l.plus * l.minus * (c.plus - c.minus)
    M[1, 1] = l.plus * c.plus - l.minus * c.minus

    return prefactor * M

#' Calculates step
#'
#' @export ot.sim.step
def step(eigenvalues=eigenvalues(), aValues=aValues(), alpha=alpha()):
    """
    Calculates step
    """
    l = eigenvalues
    A = aValues

    v1 = np.array([-1, l.plus])
    v2 = np.array([1, -l.minus])

    partA = (A.plus * v1 + A.minus * v2) * np.sqrt(1 + alpha) * np.random.randn()
    partB = (A.plus * v1 - A.minus * v2) * np.sqrt(1 - alpha) * np.random.randn()

    # keep in mind that:
    # deltaX = partA[0] + partB[0]
    # deltaV = partA[1] + partB[1]
    step = partA + partB

    return step


def simulate_trap(dataPoints=1e3,
                  timeStep=0.001,
                  radius=1000,
                  viscosity=2e5,
                  trapStiffness=0.1,
                  material="polystyrene",
                  temperature=25):
    """
    Simulates the position time series of a sphere in an optical trap

    Parameters
    ----------
    dataPoints : int
        Number of data points in final time series
        Default: 10000

    timeStep : float
        Difference between two time points; delta time
        Default: 0.001
    """
    assert timeStep > 0
    assert radius > 0
    assert dataPoints > 0

    # boundary conditions
    drag = drag_sphere(radius=radius)
    mass = mass_sphere(radius=radius)

    l = eigenvalues(dragCoefficient=drag, massSphere=mass, trapStiffness=trapStiffness)

    c = cValues(eigenvalues=l, timeStep=timeStep)

    expM = exp_Matrix(eigenvalues=l, cValues=c).T

    A = aValues(dragCoefficient=drag, eigenvalues=l, cValues=c)

    alphaValue = alpha(eigenvalues=l, cValues=c)

    state = np.zeros((dataPoints, 3))
    state[:, 0] = np.arange(0, timeStep * dataPoints, timeStep)

    for i in range(int(dataPoints) - 1):

        singleStep = step(eigenvalues=l, aValues=A, alpha=alphaValue)

        state[i + 1, 1:3] = state[i, 1:3] * expM + singleStep

    state = pd.DataFrame(state, columns=['t', 'x', 'v'])
    return state
