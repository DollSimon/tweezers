#!/usr/bin/env python
#-*- coding: utf-8 -*-

# from numba import jit
try:
    import numbapro as nb
except:
    import numba as nb

import numpy as np
# from parakeet import jit


# @nb.autojit
def pwc_bilateral(Y, beta=200, width=5, maxIter=50, stopTolerance=1e-3,
                  softKernel=1):
    """
    Performs piecewise constant denoising of the input signal using hard or
    soft bilateral filtering

    Parameters
    ----------
    Y : Numpy array
        Original signal to denoise, length N
    beta : number, default 200
        Kernel parameter. If soft Gaussian kernel, then this is the precision
        parameter. If hard kernel, this is the kernel support
    width : number, default 5
        Spatial kernel width W
    maxIter : int, default 50
        Maximum number of iterations
    stopTolerance : number, default 1e-3
        Precision of estimate as determined by square magnitude of the change
        in the solution.
    softKernel : int, default = 1
        Kernel, either 'soft' (1) or 'hard' (0)

    Returns
    -------
    X : Numpy array
        Denoised output signal

    """
    N = Y.size

    # Initial guess using the input signal
    X_old = Y.copy()

    # Pre-allocate arrays
    X = np.zeros(shape=(N))
    X_new = np.zeros(shape=(N))

    W = np.zeros(shape=(N, N))
    D = np.zeros(shape=(N, N))
    K = np.zeros(shape=(N, N))

    # Construct bilateral sequence kernel
    for i in xrange(N):
        W[i, ] = (abs(np.repeat(i, N) - xrange(N)) <= width).astype(int)

    # Iterate
    count = 1
    gap = float("inf")
    while count < maxIter:

        # print("Count: {}".format(count))
        # print("X_old: {}".format(X_old))

        # Compute pairwise distance between all samples
        for i in range(N):
            # print("i, X_old: {}, {}".format(i, X_old))
            # import ipdb; ipdb.set_trace()
            D[..., i] = 0.5 * (X_old - X_old[i]) ** 2
            # print("D: {}".format(D))

        # Compute kernels
        if softKernel:
            K = np.exp(-beta * D) * W
        else:
            K = (D <= beta ** 2) * W

        # Do kernel weighted mean shift, update step
        X_new = (K.T * X_old).sum(axis=1) / K.sum(axis=1)

        gap = np.sum((X_old - X_new) ** 2)

        # print("Gap: {}".format(gap))
        if gap < stopTolerance:
            break

        X_old = X_new.copy()
        count += 1

    X = X_new

    return X
