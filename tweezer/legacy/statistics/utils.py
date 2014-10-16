__doc__ = """\
Statistical helper functions.
"""

import numpy as np


def corrcoef(x, y, maxlag=None):
    """
    Compute the correlation coefficients of two one dimensional arrays with a given maximum lag.\
    The input vectors are converted to numpy arrays.
    http://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient
    Or see: Chatfield, 2004, The analysis of time series

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

    # pre-computing mean and denominator
    mx = np.mean(x)
    my = np.mean(y)
    denom = np.sqrt(np.sum((x - mx)**2) * np.sum((y - my)**2))

    # compute correlation coefficient for each lag
    for i in range(maxlag + 1):
        dx = x[:len(x)-i] - mx
        dy = y[i:] - my
        nom = np.sum(dx * dy)
        res[i] = nom / denom
    return res