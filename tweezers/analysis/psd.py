import tweezers.ixo.fit
from scipy.signal import welch
import pandas as pd
import numpy as np
from collections import OrderedDict


class PsdComputation:
    """
    Object to compute a PSD using Welch's method (:func:`scipy.signal.welch`).
    """

    def __init__(self, timeSeries, blockLength=1E4, samplingRate=100000, overlap=None, nBlocks=None,
                 blockData=False, axes=None):
        """
        Constructor for PsdAnalysis

        Args:
            timeSeries (:class:`pandas.DataFrame`): dataframe, PSD will be computed for each column
            blockLength (`float`): number of data points per block
            samplingRate (`float`): sampling frequency of the time series data in [Hz]
            overlap (`int`): The number of datapoints that should overlap. If not ``None``, this will take precedence
                           over ``nBlocks``. If nothing is given, the overlap is 0.
            nBlocks (`int`): The number of blocks determines the overlap between them. If set to ``None``, the number
                           is computed such that the overlap is 0.
            blockData (`bool`): Should the PSD for each block also be returned?
            axes (`list`): for which axes in the timeSeries to calculate the PSD, do it for all if ``None``
        """

        self.timeSeries = timeSeries
        self.blockLength = int(blockLength)
        self.samplingRate = samplingRate
        if overlap:
            self.overlap = int(overlap)
        else:
            self.overlap = overlap
        self.nBlocks = nBlocks
        self.blockData = blockData
        self.axes = axes

    def psd(self):
        """
        Compute the PSDs for all axes in the data object. The units of the PSD are ``<time series units>² /
        <samplingFreq units>``.

        Returns:
            :class:`pandas.DataFrame`
        """

        lenData = len(self.timeSeries.ix[:, 0])

        # get nBlocks
        if self.overlap:
            # if overlap was given, it has priority over nBlocks
            self.nBlocks = lenData // (self.blockLength - self.overlap)
        elif self.nBlocks:
            # else, compute overlap from nBlocks
            self.overlap = self.blockLength - lenData / self.nBlocks
        else:
            # default: no overlap
            self.overlap = 0
            self.nBlocks = lenData // self.blockLength

        # list of columns to go through
        cols = self.axes if self.axes else list(self.timeSeries.columns)
        cols = [x for x in cols if x not in ['t', 'time', 'absTime', 'mz']]

        psd = pd.DataFrame()
        for title, column in self.timeSeries.items():
            # ignore columns if present
            if title not in cols:
                continue

            psdRaw = self.computePsd(column,
                                     samplingFreq=self.samplingRate,
                                     blockLength=self.blockLength,
                                     overlap=self.overlap)

            # store psd, overwrites 'f' but it should be the same for all the axes so no problem here
            psd['f'] = psdRaw[0]
            psd[title] = psdRaw[1]
            psd[title + 'Std'] = psdRaw[2]

        psdMeta = OrderedDict([('psdBlockLength', self.blockLength),
                               ('psdNBlocks', self.nBlocks),
                               ('psdOverlap', self.overlap)])

        return psdMeta, psd

    def overlap(self, data):
        """
        Calculate window overlap from length of each window (block), their number and the total number of data
        points. The overlap is given in number of datapoints.

        Returns:
            :class:`int`
        """
        overlap = self.blockLength - len(data) / self.nBlocks
        if overlap < 0:
            print(str(self.blockLength) + ' ' + str(len(data)) + ' ' + str(self.nBlocks))

        return overlap
    
    @staticmethod
    def computePsd(data, samplingFreq=100000, blockLength=1E4, overlap=0):
        """
        Compute the PSD using :func:`scipy.signal.welch` for each block but do the averaging of the blocks in this
        function. This allows to also return the standard deviation of the data for each frequency and the individual
        values as well.
        
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
        """

        # the size of each step
        stepSize = blockLength - overlap
        # container to store result
        psdList = []
        for n in range(blockLength, len(data) + 1, stepSize):
            # get individual block psd and add it to our list
            f, psd = welch(data[n - blockLength:n], fs=samplingFreq, nperseg=blockLength, noverlap=overlap,
                           window='boxcar')
            # append PSD to list but exclude f = 0
            psdList.append(psd[1:])
        f = f[1:]
        psdList = np.array(psdList)
        # averaged psd
        psdAv = psdList.mean(axis=0)
        # use ddof=1 to compute the std by dividing by (n-1) (sample standard deviation)
        psdStd = np.std(psdList, axis=0, ddof=1)

        return f, psdAv, psdStd, psdList


class PsdFitMle(tweezers.ixo.fit.Fit):
    """
    Perform a maximum likelihood fit as described in the Norrelyke paper.
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


class PsdFit:
    """
    Fit the PSD.
    """

    def __init__(self, psd, fitCls=tweezers.ixo.fit.LeastSquaresFit, minF=5, maxF=7*10**3, residuals=True, **fitargs):
        """
        Constructor for PsdFit

        Args:
            psd (:class:`pandas.DataFrame`): data container, data columns ending with ``Std`` are interpreted as
                                             standard deviation of the data with the otherwise same column name and
                                             used for weighted fits, a column ``f`` must be present with the frequency
                                             values
            fitCls (:class:`tweezers.ixo.fit.Fit`): class to use for fitting, must implement the methods given in the
                                            reference class
            minF (`float`): only data points with frequencies above this limit are fitted
            maxF (`float`): only data points with frequencies below this limit are fitted
            residuals (`bool`): compute the residuals for the fit, they are added as columns to the PSD fit data
            others: additional arguments are passed on to the constructor of ``fitCls``
        """

        self.psd = psd
        # fit class to use
        self.fitCls = fitCls
        # fit limits
        self.minF = minF
        self.maxF = maxF
        self.residuals = residuals
        self.fitargs = fitargs

        # hold fit results when required
        self.fitObj = {}
        self.D = {}
        self.fc = {}
        self.std = {}
        self.r2 = {}
        self.chi2 = {}

    def fit(self):
        """
        Fit the PSD with the fitting class given in the constructor. Note that the value stored under ``PsdFitError``
        returned meta data can describe different things depending on the fitting class used.

        Returns:
             * fitParams (:class:`dict`) -- fit parameters and metadata as dictionary
             * psdFit (:class:`pandas.DataFrame`) -- data of the fitted curve
        """

        # check for frequency column
        if 'f' not in self.psd.columns:
            raise ValueError('No frequency data found. The column must be called "f".')

        # select data based of frequency limits for fitting
        freqQuery = '{} <= f <= {}'.format(self.minF, self.maxF)
        psd = self.psd.query(freqQuery)
        # dataframe to hold result
        psdFit = psd[['f']].copy()
        # hold fitting parameters
        fitParams = OrderedDict()

        for axis, column in psd.iteritems():
            # skip columns ending on 'Std', they contain error data
            if axis.lower().endswith('std') or axis is 'f':
                continue

            # check for column with error data
            if axis + 'Std' in psd.columns:
                psdStd = psd[axis + 'Std']
            else:
                psdStd = None

            # create fit object and do the fit
            fitObj = self.fitCls(psd['f'],
                                 psd[axis],
                                 fcn=self.lorentzian,
                                 std=psdStd,
                                 **self.fitargs)

            # get results
            D = fitObj.coef[0]
            fc = fitObj.coef[1]

            # append fitted Lorentzian x and y data to to fit-dataframe
            psdFit.loc[:, axis + 'Fit'] = self.lorentzian(psdFit['f'], D, fc)

            fitParams[axis] = OrderedDict()
            fitParams[axis]['diffusionCoefficient'] = D
            fitParams[axis]['cornerFrequency'] = fc
            fitParams[axis]['psdFitError'] = list(fitObj.fitError)  # convert to list for conversion to JSON
            fitParams[axis]['psdFitR2'] = fitObj.rsquared()
            # chi2 can only be computed if std data is given
            if psdStd is not None:
                fitParams[axis]['psdFitChi2'] = fitObj.chisquared()

            # compute residuals if required
            if self.residuals:
                psdFit.loc[:, axis + 'Residuals'], meanResidual = fitObj.residuals()
                fitParams[axis]['psdFitMeanResidual'] = meanResidual

        fitParams['psdFitMinF'] = self.minF
        fitParams['psdFitMaxF'] = self.maxF

        return fitParams, psdFit

    @staticmethod
    def lorentzian(f, D, fc):
        """
        Lorentzian function

        Args:
            f (:class:`numpy.array`): frequency in units of [Hz]
            D (`float`): diffusion constant in units of [V]
            fc (`float`): corner frequency in units of [Hz]

        Returns:
            :class:`numpy.array`
        """

        return D / (np.pi ** 2 * (f ** 2 + fc ** 2))