__doc__ = """\
Statistical helper functions.
"""

import numpy as np


def corrcoef(x, y, maxlag=None):
    """
    Compute the correlation coefficients of two one dimensional arrays with a given maximum lag.\
    The input vectors are converted to numpy arrays.

    Args:
        x (array_like): one dimensional input array
        y (array_like): one dimensional input array
        maxlag (int): maximum lag (default is len(x)//4)

    Returns:
        (:class:`numpy.array`) A one dimensional vector of length maxlag + 1 (to account for zero lag).
    """

    if maxlag is None:
        maxlag = len(x) // 4

    # convert input to numpy array for speed
    x = np.array(x)
    y = np.array(y)

    # prepare output array
    res = np.zeros(maxlag + 1)
    # check length of y
    if len(y) < maxlag + 1:
        raise ValueError('y array is too short.')

    # compute correlation coefficient for each lag
    for i in range(maxlag + 1):
        dx = x[:len(x)-i] - np.mean(x[:len(x)-i])
        dy = y[i:] - np.mean(y[i:])
        nom = np.sum(dx * dy)
        denom = np.sqrt(np.sum(dx**2) * np.sum(dy**2))
        res[i] = nom / denom
    return res