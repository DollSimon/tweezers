import numpy as np
import scipy as sp
import logging as logging
import scipy.signal # scipy import bug?

import tweezers.ixo.fit as fit
import tweezers.physics.tweezers as tp


def computePsd(data, samplingFreq=100000, blockLength=10000, overlap=0):
    """
    Compute the PSD (power spectral density) by dividing the full time series into blocks, computing the PSD for each
    block and averaging the result across blocks.

    The PSD is computed using `Welch's method`_ (via :func:`scipy.signal.welch`).
    This function also returns the standard deviation of the averaged PSD data and the PSD computed for each block.

    Args:
        data (array-like): 1-D data array
        samplingFreq (`int`): sampling frequency of the data
        blockLength (`int`): number of data points per block
        overlap (`int`): number of overlapping data points of consecutive blocks

    Returns:
        * frequency (:class:`numpy.ndarray`)
        * PSD values (:class:`numpy.ndarray`)
        * PSD standard deviation (:class:`numpy.ndarray`)
        * PSD values for each block

    .. _Welch's method:
        https://en.wikipedia.org/wiki/Welch%27s_method
    """

    # the size of each step
    stepSize = blockLength - overlap
    # container to store result
    psdList = []
    for n in range(blockLength, len(data) + 1, stepSize):
        # get individual block psd and add it to our list
        f, psd = sp.signal.welch(data[n - blockLength:n], fs=samplingFreq, nperseg=blockLength, noverlap=0,
                                 window='boxcar')
        # append PSD to list but exclude f = 0
        psdList.append(psd[1:])
    f = f[1:]
    psdList = np.array(psdList)
    # averaged psd
    psdAv = psdList.mean(axis=0)
    # use ddof=1 to compute the std by dividing by (n-1) (sample standard deviation)
    psdStd = np.std(psdList, axis=0, ddof=1)

    res = {'f': f, 'psdMean': psdAv, 'psdStd': psdStd,
           'blockLength': blockLength, 'nBlocks': len(psdList), 'overlap': overlap}

    return res, psdList


def computePsdBlocking(data, samplingFreq=100000, nblocks=100, log=True):
    """
    Compute the PSD (power spectral density) by dividing the full time series into blocks, computing the PSD for each
    block and averaging the result across blocks. This is described by `Berg-Sørensen et al.`_: "Power spectrum analysis
    for optical tweezers".

    The PSD is computed using `Welch's method`_ (via :func:`scipy.signal.welch`).
    This function also returns the standard deviation of the averaged PSD data and the PSD computed for each block.

    Note that in the software, that comes with the paper, does the blocking in natural-logarithm space but plots the
    PSD in common-logarithm (base 10) space. It is recommended what is the right procedure. Note that this code does the
    blocking in common-logarithm space and it is not clear if this is correct!!! Check this before using this code!!!

    Args:
        data (array-like): 1-D data array
        samplingFreq (`int`): sampling frequency of the data
        nblocks (`int`): number of blocks
        log (`bool`): blocking in log-space? (equal width in normal or log-space)

    Returns:
        * frequency (:class:`numpy.ndarray`)
        * PSD values (:class:`numpy.ndarray`)
        * PSD standard deviation (:class:`numpy.ndarray`)
        * PSD values for each block


    .. _Berg-Sørensen et al.:
        https://doi.org/10.1063/1.1645654
    .. _Welch's method:
        https://en.wikipedia.org/wiki/Welch%27s_method
    """

    logging.warning('Check if blocking is implemented properly! Read the docstring of this function!')

    # compute power spectrum fro complete dataset
    f, psd = sp.signal.welch(data, fs=samplingFreq, nperseg=len(data), noverlap=0, window='boxcar')
    # remove f = 0 data
    psd = psd[1:]
    f = f[1:]

    # binning
    if log:
        # in logspace
        bins = np.exp(np.linspace(np.log(f[0]), np.log(f[-1]), nblocks + 1, endpoint=True))
    else:
        bins = np.linspace(f[0], f[-1], nblocks + 1, endpoint=True)

    psdav = {'f': [], 'psdMean': [], 'psdStd': [], 'n': []}
    for i in range(len(bins) - 1):
        idx = (f >= bins[i]) & (f < bins[i + 1])
        n = np.sum(idx)
        if n > 0:
            psdav['f'] += [np.nanmean(f[idx])]
            psdav['psdMean'] += [np.nanmean(psd[idx])]
            if n == 1:
                psdav['psdStd'] += [np.nan]
            else:
                psdav['psdStd'] += [np.nanstd(psd[idx], ddof=1)]
            psdav['n'] += [n]

    return psdav


class PsdFit(fit.LeastSquaresFit):
    """
    Class for fitting the PSD using least squares fitting via :class:`tweezers.ixo.fit.LeastSquaresFit`.
    """

    def __init__(self, f, psd, minF=10, maxF=40000, diode=False, peakF=0, **kwargs):
        """

        Args:
            f (:class:`numpy.ndarray`): frequency data
            psd (:class:`numpy.ndarray`): PSD data
            minF (`float`): minimum fitting frequency
            maxF (`float`): maximum fitting frequency
            diode (`bool`): fit with taking diode effects into account?
            peakF (`float`): frequency of the peak if using the oscillation calibration method
            **kwargs: additional arguments are passed to the constructor of the parent class
        """

        fitfcn = tp.lorentzian
        if diode:
            fitfcn = tp.psdDiode
            # fitting the diode-corrected PSD with weighting requires initial parameters or often fails otherwise
            if 'p0' not in kwargs.keys():
                kwargs['p0'] = [1000, 0.2, 2000, 0.5]

        kwargs['fcn'] = fitfcn

        # select fitting data
        idx = (f >= minF) & (f <= maxF)
        self.fFull = f[idx]

        if peakF > 0:
            idx = idx & (f != peakF)

        x = f[idx]
        y = psd[idx]

        if 'std' in kwargs.keys():
            kwargs['std'] = kwargs['std'][idx]

        super().__init__(x, y, **kwargs)

    def fitresAsMeta(self):
        """
        Get fit results (parameters) as a dictionary.

        Returns:
            `dict`
        """

        meta = {}
        meta['cornerFrequency'] = self.coef[0]
        meta['diffusionCoefficient'] = self.coef[1]

        if self.fcn == tp.psdDiode:
            meta['diodeF3db'] = self.coef[2]
            meta['diodeA'] = self.coef[3]

        meta['psdFitR2'] = self.rsquared
        meta['psdFitResidual'] = self.meanResidual
        if (self.std is not None) and any(self.std):
            meta['psdFitChi2'] = self.chisquared

        return meta

    @property
    def yFitFull(self):
        """
        Attribute to hold the full PSD with the fitted coefficients. This will include the value for the peak that was
        excluded during fitting (required for oscillation method).

        Returns:
            :class:`list` of :class:`float`, depending on the input
        """

        fit = self.fcn(self.fFull, *self.coef)
        return fit

    def fit(self):
        try:
            res = super().fit()
        except RuntimeError:
            res = np.full(4, np.nan)
            self.fitError = np.full(4, np.nan)
            logging.warning('PSD fit failed!')

        return res


class PsdFitMle(fit.Fit):
    """
    Perform a maximum likelihood fit as described in the Norrelyke paper.
    Needs checking!!
    """

    def __init__(self, *args, nBlocks, **kwargs):
        """
        Constructor for PsdFitMle

        Args:
            container (:class:`tweezers.container.TweezersData`): data container
            nBlocks (`int`): number of blocks in the PSD
        """

        super().__init__(*args, **kwargs)
        self.nBlocks = nBlocks

    def fit(self):
        """
        Do the fit following the linear approximation of Norrelyke paper

        Returns:
            D (`float`): diffusion constant
            fc (`float`): corner frequency
        """

        s = self.mleFactors(self.y)
        a, b = self.mleAB(s, self.nBlocks)
        D, fc = self.mleParameters(a, b, self.nBlocks)
        self.fitResult = [D, fc]

        self.fitError = self.mleErrors(D, fc, a, b, self.nBlocks)

        return self.fitResult

    def mleFactors(self, P):
        """
        Calculation of the S coefficients related to the MLE, according to the paper of Norrelyke

        Args:
            P (:class:`numpy.array`): Experimental PSD function in [V^2]

        Returns:
            s (`list` of `float`) -- matrix with the S coefficients
        """

        nFreq = len(self.x)
        s01 = 1/nFreq * np.sum(P)
        s02 = 1/nFreq * np.sum(np.power(P, 2))
        s11 = 1/nFreq * np.sum(np.multiply(np.power(self.x, 2), P))
        s12 = 1/nFreq * np.sum(np.multiply(np.power(self.x, 2), np.power(P, 2)))
        s22 = 1/nFreq * np.sum(np.multiply(np.power(self.x, 4), np.power(P, 2)))
        s = [[0, s01, s02], [0, s11, s12], [0, s12, s22]]

        return s

    def mleAB(self, s, n):
        """
        Calculation of the pre-parameters a and b, according to the paper of Norrelyke

        Args:
            s (`list` of `float`): matrix with the S coefficients
            n (`float`): number of averaged power spectra (total data points divided by the block length)

        Returns:
            a, b (`float`) -- pre-parameters for the calculation of D and fc
        """

        a = ((1+1/n)/(s[0][2]*s[2][2]-s[1][2]*s[1][2])) * (s[0][1]*s[2][2]-s[1][1]*s[1][2])
        b = ((1+1/n)/(s[0][2]*s[2][2]-s[1][2]*s[1][2])) * (s[1][1]*s[0][2]-s[0][1]*s[1][2])
        return a, b

    def mleParameters(self, a, b, n):
        """Calculate parameters from the factors of the MLE

        Args:
            a (`float`): pre-parameter for the calculation of D and fc
            b (`float`): pre-parameter for the calculation of D and fc
            n (`float`): number of averaged power spectra (total data points divided by the block length)

        Returns:
            * D (float) -- diffusion constant in units of [V]
            * fc (float) -- corner frequency in units of [Hz]

        """

        if a*b > 0:
            fc = np.sqrt(a/b)
        else:
            fc = 0
        D = (n * np.pi**2/(n+1)) / b

        return D, fc

    def mleErrors(self, D, fc, a, b, n):
        """
        Function to get the standard deviation of the parameters according to the paper of Norrelyke

        Args:
            f (:class:`numpy.array`): array of the frequencies in units of [Hz]
            D (`float`): diffusion constant in units of [V]
            fc (`float`): corner frequency in units of [Hz]
            a, b (`float`): pre-parameters for the calculation of D and fc
            n (`float`): number of averaged power spectra (total data points divided by the block length)

        Returns:
            errosMle (:class:`numpy.array`) -- with sigma(D) and sigma(fc)
        """

        s = self.mleFactors(self.yFit)
        sB = [[(n+1)/n*s[0][2], (n+1)/n*s[1][2]], [(n+1)/n*s[1][2], (n+1)/n*s[2][2]]]
        sError = 1/(len(self.x)*n)*(n+3)/n*np.linalg.inv(sB)

        sigmaFc = fc**2/4 * (sError[0][0]/a**2+sError[1][1]/b**2-2*sError[0][1]/(a*b))
        sigmaD = D**2*(sError[1][1]/b**2)
        errorsMle = [np.sqrt(sigmaD), np.sqrt(sigmaFc)]

        return errorsMle
