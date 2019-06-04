import numpy as np
import pandas as pd


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
    meanX = np.mean(x)
    stdX = np.std(x, ddof=ddof)
    meanY = np.mean(y)
    stdY = np.std(y, ddof=ddof)

    res = np.zeros((length + 1, 2))
    # calculate first column values
    res[:, 0] = np.arange(length + 1)

    res[0, 1] = corr_coeff(x, y, meanX, meanY, stdX, stdY)
    for i in range(1, length + 1):
        res[i, 1] = corr_coeff(x[i:], y[:-i], meanX, meanY, stdX, stdY)

    return res


def cdf(data):
    """
    Computes the cumulative density function (or cumulative probability) of the given data
    """
    
    x = np.sort(np.array(data))
    y = np.arange(1, len(x) + 1) / len(x)
    return x, y


def binData(data, binningAxis, bins=100):
    if isinstance(bins, int):
        bins = np.linspace(data[binningAxis].min(), data[binningAxis].max(), bins)
    elif len(bins) == 3:
        bins = np.linspace(*bins)
    # else assume bin limits are given

    # get center of each bin as label
    labels = bins[:-1] + np.diff(bins) / 2

    data['binned'] = pd.cut(data[binningAxis], bins=bins, labels=labels)
    res = data.groupby('binned', as_index=False).mean()

    return res, labels


def traceBootstrap(data, n=1000, ci=95, interpolation='nearest'):
    """
    data: each row is an observation, columns are data bins
    """

    nSamples = data.shape[0]
    bsRes = np.zeros((n, data.shape[1]))
    for i in range(n):
        # pick random sample from data with replacing
        bs = data[np.random.randint(nSamples, size=nSamples)]
        bsRes[i, :] = np.nanmean(bs, axis=0)

    mean = np.nanmean(bsRes, axis=0)
    if ci == 'std':
        bsStd = np.nanstd(bsRes, axis=0)
        lower = mean - bsStd
        upper = mean + bsStd
    else:
        lower = np.nanpercentile(bsRes, 100 - ci, axis=0, interpolation=interpolation)
        upper = np.nanpercentile(bsRes, ci, axis=0, interpolation=interpolation)

    return mean, lower, upper