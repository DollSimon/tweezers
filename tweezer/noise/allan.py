#!/usr/bin/env python

import pandas as pd
from numpy import (log10, zeros, sqrt, floor, ceil, array, mean, sum, diff, empty, float)
from numba import jit


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


def allan_variance(data, dt=1):
    """
    Compute the Allan variance on a set of regularly-sampled data (1D).

       If the time between samples is dt and there are N total
       samples, the returned variance spectrum will have frequency
       indices from 1/dt to (N-1)/dt.

    """
    # 2008-07-30 10:20 IJC: Created
    # 2011-04-08 11:48 IJC: Moved to analysis.py
    # 2011-10-27 09:25 IJMC: Corrected formula; thanks to Xunchen Liu
    #                        of U. Alberta for catching this.

    newdata = array(data, subok=True, copy=True)
    dsh = newdata.shape

    newdata = newdata.ravel()

    nsh = newdata.shape

    alvar = zeros(nsh[0]-1, float)

    for lag in range(1, nsh[0]):
        # Old, wrong formula:
        #alvar[lag-1]  = mean( (newdata[0:-lag] - newdata[lag:])**2 )
        alvar[lag-1] = (mean(newdata[0:(lag+1)])-mean(newdata[0:lag]))**2

    return (alvar*0.5)



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
    # print("Core")
    # print("N: {}".format(N))
    # print("M: {}".format(M))
    # print("N - M + 1: {}".format(N - M + 1))
    # print("D.shape: {}".format(D.shape))
    D[0] = sum(data[0:M]) / M

    for i in range(1, N - M + 1):
        D[i] = D[i - 1] + (data[i + M - 1] - data[i - 1]) / M

    return 0.5 * mean(diff(D[0:N - M + 1:M])**2)


@jit
def allan_variances(inData, tau, rate):
    """
    Calculates the Allan variance of a time series.

    """
    N = inData.shape[0]
    J = tau.shape[0]
    A = empty(J, dtype=float)
    D = empty(N, dtype=float)
    M = floor(tau * rate).astype(int)

    # print("N: {}".format(N))
    # print("J: {}".format(J))
    # print("M: {}".format(M))
    # print("len(M): {}".format(len(M)))
    # print("A.shape[0]: {}".format(A.shape[0]))

    for j in range(J):

        A[j] = core_allan(inData, D, M[j], N)

    return A


def generate_allan_tau(inData, rate):

    firstTau = 1 / rate

    N = inData.shape[0]
    n = int(ceil((N - 1) / 2))
    p = int(floor(log10(n) / log10(2)))

    tau = [(2**i) * firstTau for i in range(p + 1)]

    return array(tau)

