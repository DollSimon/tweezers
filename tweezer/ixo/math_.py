#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import print_function, division

import numpy as np

from numba.decorators import autojit


@autojit
def map_array_to_range(X):
    """
    Maps (normalises) an array to range specified
    :param X: (numpy.array) of shape (M, N)
    :param map_range: (list of two numbers)

    :return S: (numpy.array) normalised array of shape (M, N), mapped to \
    range specified
    """
    map_range = [-1, 1]

    M = X.shape[0]
    N = X.shape[1]

    maxX = np.max(X)
    minX = np.min(X)

    minR = min(map_range)
    maxR = max(map_range)

    spanX = maxX - minX
    spanR = maxR - minR

    slope = spanR / spanX

    S = np.empty((M, N), dtype=np.float)

    for i in xrange(M):
        for j in xrange(N):
            S[i, j] = ((X[i, j] - minX) * slope) + minR

    return S


def isEven(number):
    return (number) & (number - 1) == 0
