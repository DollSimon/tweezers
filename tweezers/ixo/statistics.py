import numpy as np
import pandas as pd


def average(data, nsamples=10, fcn=np.mean):
    """
    Downsample the given 1D array by averaging `nsamples` consecutive datapoints

    Args:
        data (np.array):  1D array
        nsamples: number of samples to average
        fcn: function used to average, defaults to `numpy.mean` but can be anything that returns a single value from an
             array

    Returns:

    """
    nrows = len(data) // nsamples
    ndata = nsamples * nrows
    da = np.reshape(data[:ndata], (nrows, nsamples))
    da = fcn(da, axis=1)
    return da


def averageDf(data, by='time', nsamples=10):
    """
    Downsample the data by first sorting the `pandas.DataFrame` by ``by`` and then averaging ``nsamples`` consecutive
    datapoints.

    Args:
        data (`pandas.DataFrame`): data to average
        by (`str`): column used for sorting
        nsamples (`int`): number of samples to average

    Returns:
        :class:`pandas.DataFrame`
    """

    ds = data.sort_values(by)
    groupIdx = np.arange(ds.shape[0]) // nsamples
    group = ds.groupby(groupIdx)
    avData = group.mean()
    
    # avData['time'] = group.first()['time']
    # if 'absTime' in data.columns:
    #     avData['absTime'] = group.first()['absTime']

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
    Computes the cumulative density function (or cumulative probability) of the given data.

    Args:
        data (np.array): 1D array

    Returns:

        * x (:func:`numpy.array`) - bins
        * y (:func:`numpy.array`) - cumulative probability for each bin
    """

    x = np.sort(np.array(data))
    y = np.arange(1, len(x) + 1) / len(x)
    return x, y


def binDf(data, binningAxis, bins=100, binWidth=None):
    """
    Bin the data in a `pandas.DataFrame` by the given axis.

    Args:
        data (:class:`pandas.DataFrame`): data to bin
        binningAxis (str): name of the axis to use for binning
        bins: can be 1) an integer number of bins to use, 2) an array of 3 numbers passed to :func:`numpy.linspace` or
              3) an array of bin limits
        binWidth: use a fixed width to determine the bins, if set this input is preferred over the `bins` argument

    Returns:
        :class:`pandas.DataFrame`
    """

    # if binWidth is given, use to determine bins
    if binWidth:
        mi = data[binningAxis].min()
        ma = data[binningAxis].max()
        bins = int(np.ceil((ma - mi) / binWidth))

    if isinstance(bins, int):
        bins = np.linspace(data[binningAxis].min(), data[binningAxis].max(), bins)
    elif len(bins) == 3:
        bins = np.linspace(*bins)
    # else assume list of limits for each bin is given

    # get center of each bin as label
    labels = bins[:-1] + np.diff(bins) / 2

    binnedData = data.copy()
    binnedData[binningAxis] = pd.cut(binnedData[binningAxis], bins=bins, labels=labels)
    binnedData = binnedData.groupby(binningAxis, as_index=False).mean()
    binnedData[binningAxis] = binnedData[binningAxis].astype(data[binningAxis].dtype)

    return binnedData


def traceBootstrap(data, n=1000, ci=95, interpolation='nearest'):
    """
    Bootstrap a trace

    Args:
        data (:func:`numpy.array`): an 2D array where each column is a datapoint of a 1D array and each row is an observation
        n (int): number of bootstrapping samples
        ci (int): confidence interval: either 'std' to use mean +/- standard deviation or a value from 0 to 100 used as a percentile
        interpolation (str): interpolation method used by :func:`numpy.nanpercentile`

    Returns:

        * mean (:func:`numpy.array`) - 1D array with mean values of bootstrapped data
        * lower (:func:`numpy.array`) - 1D array with lower bound of confidence interval
        * upper (:func:`numpy.array`) - 1D array with upper bound of confidence interval
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


def allanVar(data, dt, t=(-5, 1, 100)):
    """
    Compute the Allan variance.

    Args:
        data (:func:`numpy.array`): array holding the data for which to compute the Allan variance
        dt (float): time resolution of the data; in other words the time difference between consecutive data points in
                    `data`
        t (list): tuple with 3 values used as input for :func:`numpy.logspace` which determines the array of time shifts
                  for which to calculate the Allan variance

    Returns:

        * tRange (:func:`numpy.array`) - time shift array
        * var (:func:`numpy.array`) - Allan variance for each shift
    """

    tRange = np.logspace(*t)
    var = []
    for t in tRange:
        n = (t / dt).round().astype(int)
        da = average(data, nsamples=n)
        if len(da) <= 2:
            varT = np.nan
        else:
            varT = np.nanmean(np.diff(da) ** 2)
        var.append(varT)
    var = 0.5 * np.array(var)
    return tRange, var


def allanVarDf(x, data, t=(-5, 1, 100)):
    """
    Compute the Allan variance for a :class:`pandas.DataFrame`.

    Args:
        x (str): name of the column in `data` for which to compute the Allan variance
        data (:class:`pandas.DataFrame`): data, requires a column named 'time'
        t (list): tuple with 3 values used as input for :func:`numpy.logspace` which determines the array of time shifts
                  for which to calculate the Allan variance

    Returns:
        :class:`pandas.DataFrame`
    """

    dt = data.time.diff().mean()
    d = data[x].values

    tRange, var = allanVar(data[x].values, dt, t=t)
    res = pd.DataFrame({'time': tRange, 'allanVar': var})
    return res
