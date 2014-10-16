#!/usr/bin/env python

import pandas as pd
from numpy import (log10, zeros, sqrt, floor, ceil, array, mean, sum, diff, empty, float)
from numba import jit

try:
    from tweezer.legacy.physics2 import thermal_energy
except ImportError as err:
    print('The tweezer package has not been correctly installed or updated.')
    raise err


# Calculations of actual time series ----

def allan_variance_r_port(data, frequency):
    """
    Calculates the allan variance.
    """

    N = len(data)
    tau = 1 / frequency

    n = int(ceil((N - 1) / 2))
    p = int(floor(log10(n) / log10(2)))

    av = zeros(p + 1)
    time = zeros(p + 1)
    error = zeros(p + 1)

    print("Calculation: ")

    for i in range(p + 1):

        omega = zeros(int(floor(N / 2 ** i)))
        T = (2 ** i) * tau
        l = 0
        k = 0

        while k <= int(floor(N / (2 ** i))):

            try:
                omega[k] = sum(data[l:(l + ((2 ** i) - 1))]) / (2 ** i)
            except (TypeError, IndexError):
                pass

            l += 2 ** i
            k += 1

        sumvalue = 0

        for k in range(len(omega) - 1):
            sumvalue += omega[k + 1] - omega[k] ** 2

        av[i] = sumvalue / (2 * (len(omega) - 1))
        time[i] = T
        error[i] = 1 / sqrt(2 * ((N / (2 ** i)) - 1))

    allanVariances = pd.DataFrame({'av': av, 'error': error}, index=time)

    return allanVariances


@jit('f8(f8[:], f8[:], uint8, uint16)')
def core_allan(data, D, M, N):
    """
    Core of the Allan variance calculation according to \
    Fabian Czerwinsky's Matlab code. This makes use of numba.

    :param data: time series
    :type data: numpy.array

    :param D: 1D container to do calculations
    :type D: numpy.array

    :param M:
    :type M: int

    :param N: number of data points. This could be inferred from \
        data itself, but would make the numba optimisation harder to do.
    :type N: int

    :rtype: float
    """
    D[0] = sum(data[0:M]) / M

    for i in range(1, N - M + 1):
        D[i] = D[i - 1] + (data[i + M - 1] - data[i - 1]) / M

    return 0.5 * mean(diff(D[0:N - M + 1:M])**2)


@jit
def allan_variance(data, rate):
    """
    Calculates the Allan variance of a time series.

    .. todo: type checking and better documentation
    .. todo: add different versions of calculating tau values (overlapping,
    non-overlapping, etc.)
    """
    tau = generate_allan_tau(data=data, rate=rate)

    N = data.shape[0]
    J = tau.shape[0]
    A = empty(J, dtype=float)
    D = empty(N, dtype=float)
    M = floor(tau * rate).astype(int)

    for j in range(J):

        A[j] = core_allan(data, D, M[j], N)

    return A


def generate_allan_tau(data, rate):
    """
    Generates tau, or time lag, values for Allan variance calculations.
    """
    firstTau = 1 / rate

    N = data.shape[0]
    n = int(ceil((N - 1) / 2))
    p = int(floor(log10(n) / log10(2)))

    tau = [(2**i) * firstTau for i in range(p + 1)]

    return array(tau)


# Theoretical results ----

def _allan_shape_factor(N=4096, m=8):
    """

    :param N: sample size
    :type N: int

    :param m: block size
    :type m: int
    """

    N = nSamples
    m = blockSize

    return (1 / 2) * ((N / m) - 1)


def allan_variance_single_trap_thermal_limit(tau,
                               gamma = 4E-5,
                               k = 2E-4,
                               kBT = thermal_energy(),
                               asDataFrame = True):
    """
    Theoretical limit of Allan variance of a bead in an optical trap.

    .. math::

        \sigma^2(\\tau) = 2 k_{B} T \gamma / \kappa^2 \\tau

    """
    avar = 2 * kBT * gamma / (k**2 * tau)

    if asDataFrame:
        result = pd.DataFrame({"tau": tau, "avar": avar})
    else:
        result = avar

    return result


def allan_variance_single_trap(tau,
                               gamma = 4E-5,
                               k = 2E-4,
                               kBT = thermal_energy(),
                               asDataFrame = True):
    pass




