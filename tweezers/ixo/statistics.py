import numpy as np


def averageData(data, nsamples=10):
    """
    Downsample the data by averaging ``nsamples``.

    Args:
        data (`pandas.DataFrame`): data to average
        nsamples (`int`): number of samples to average

    Returns:
        :class:`pandas.DataFrame`
    """

    group = data.groupby(data.index // nsamples)
    avData = group.mean()
    avData['time'] = group.first()['time']
    if 'absTime' in data.columns:
        avData['absTime'] = group.first()['absTime']

    return avData


def correlate(x, y, length=20):
    """
    Calculate the normalized correlation coefficients of two 1-D arrays for a given maximum lag starting at 0.

    Args:
        x (np.array): first array to compute the correlation coefficients
        y (np.array): second array to compute the correlation coefficients
        length (int): maximum lag to compute the corrleation coefficients, return array will have size `length + 1`

    Returns:
        np.array
    """

    def corr_coeff(x, y, meanX, meanY, stdX, stdY):
        # this assumes x and y of same length
        return 1.0/len(x) * np.sum((x - meanX) * (y - meanY)) / (stdX * stdY)

    #TODO: check dimensions of x and y, if they are 2-D, assume that they contain x and y values

    # use corrected sample standard deviation
    ddof = 1
    meanX = np.mean(x[:, 1])
    stdX = np.std(x[:, 1], ddof=ddof)
    meanY = np.mean(y[:, 1])
    stdY = np.std(y[:, 1], ddof=ddof)

    res = np.zeros((length + 1, 2))
    # calculate first column values
    res[:, 0] = (x[1, 0] - x[0, 0]) * np.arange(length + 1)

    res[0, 1] = corr_coeff(x[:, 1], y[:, 1], meanX, meanY, stdX, stdY)
    for i in range(1, length + 1):
        res[i, 1] = corr_coeff(x[i:, 1], y[:-i, 1], meanX, meanY, stdX, stdY)

    return res