import ixo.fit
from scipy.signal import welch
import pandas as pd
from physics.tweezers import trap_stiffness, distance_calibration
import numpy as np


class PsdComputation():
    """
    Object to compute a PSD using Welch's method (:func:`scipy.signal.welch`).
    """

    def __init__(self, container, blockLength=2**13, overlap=None, nBlocks=None, blockData=False):
        """
        Constructor for PsdAnalysis

        Args:
            container (:class:`tweezer.TweezerData`): data container
            blockLength (float): number of data points per block (default: 2**13)
            overlap (int): The number of datapoints that should overlap. If not ``None``, this will take precedence
                           over ``nBlocks``. If nothing is given, the overlap is 0.
            nBlocks (int): The number of blocks determines the overlap between them. If set to ``None``, the number
                           is computed such that the overlap is 0.
            blockData (bool): Should the PSD for each block also be returned?
        """

        self.c = container
        self.blockLength = int(blockLength)
        if overlap:
            self.overlap = int(overlap)
        else:
            self.overlap = overlap
        self.nBlocks = nBlocks
        self.blockData = blockData

    def psd(self):
        """
        Compute the PSDs for all axes in the data object. The units of the PSD are directly stored in the data
        container object.

        Returns:
            :class:`pandas.DataFrame`
        """

        lenData = len(self.c.ts.ix[:, 0])

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

        psd = pd.DataFrame()
        for title, column in self.c.ts.items():
            psdRaw = self.compute_psd(column,
                                      samplingFreq=self.c.meta['samplingRateTs'],
                                      blockLength=self.blockLength,
                                      overlap=self.overlap)

            # store psd, overwrites 'f' but it should be the same for all the axes so no problem here
            psd['f'] = psdRaw[0]
            # get rid of the 'diff' at the end of the title strings, should be there by convention
            titleNew = title.split('Diff')[0]
            self.c.units[titleNew] = self.c.units[title] + '² / Hz'
            psd[titleNew] = psdRaw[1]
            psd[titleNew + 'Std'] = psdRaw[2]
            # update metadata dict
            self.c.meta.set(title, 'PsdBlockLength', self.blockLength)
            self.c.meta.set(title, 'PsdNBlocks', self.nBlocks)
            self.c.meta.set(title, 'PsdOverlap', self.overlap)

        return psd

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
    def compute_psd(data, samplingFreq=80000, blockLength=2**13, overlap=0):
        """
        Compute the PSD using :fcn:`scipy.signal.welch` for each block but do the averaging of the blocks in this
        function. This allows to also return the standard deviation of the data for each frequency and the individual
        values as well.
        
        Args:
            data (array-like): 1-D data array
            samplingFreq (int): sampling frequency of the data
            blockLength (int): number of data points per block
            overlap (int): number of overlapping data points of consecutive blocks
           
        Returns:
            frequency, PSD values, PSD standard deviation, PSD values for each block; all as :class:`numpy.ndarray`
        """

        # the size of each step
        stepSize = blockLength - overlap
        # container to store result
        psdList = []
        for n in range(blockLength, len(data) + 1, stepSize):
            # get individual block psd and add it to our list
            f, psd = welch(data[n - blockLength:n], fs=samplingFreq, nperseg=blockLength, noverlap=overlap)
            psdList.append(psd)
        psdList = np.array(psdList)
        # averaged psd
        psdAv = psdList.mean(axis=0)
        # use ddof=1 to compute the std by dividing by (n-1) (sample standard deviation)
        psdStd = np.std(psdList, axis=0, ddof=1)

        return f, psdAv, psdStd, psdList


class PsdFitLeastSquares(ixo.fit.LeastSquaresFit):
    """

    """

    def __init__(self, *args, container=None, **kwargs):
        """
        Constructor for PsdFitLeastSquares

        Args:
            container (:class:`tweezer.TweezerData`): data container

        """

        super().__init__(*args, **kwargs)
        self.c = container


class PsdFitMle(ixo.fit.Fit):
    """
    Perform a maximum likelihood fit as described in the Norrelyke paper.
    """

    def __init__(self, *args, container=None, **kwargs):
        """
        Constructor for PsdFitMle

        Args:
            container (:class:`tweezer.TweezerData`): data container
        """

        super().__init__(*args, **kwargs)
        self.c = container

    def fit(self):
        """
        Do the fit following the linear approximation of Norrelyke paper

        Returns:
            D (float): diffusion constant
            fc (float): corner frequency
        """

        # number of blocks in PSD
        n = self.c.meta['nBlocks']
        s = self.mle_factors(self.y)
        a, b = self.mle_ab(s, n)
        D, fc = self.mle_parameters(a, b, n)
        self.fitResult = [D, fc]

        self.fitError = self.mle_errors(D, fc, a, b, n)

        return self.fitResult

    def mle_factors(self, P):
        """
        Calculation of the S coefficients related to the MLE, according to the paper of Norrelyke

        Args:
            P (np.array): Experimental PSD function in [V^2]

        Returns:
            s (list of float): matrix with the S coefficients
        """

        nFreq = len(self.x)
        s01 = 1/nFreq * np.sum(P)
        s02 = 1/nFreq * np.sum(np.power(P, 2))
        s11 = 1/nFreq * np.sum(np.multiply(np.power(self.x, 2), P))
        s12 = 1/nFreq * np.sum(np.multiply(np.power(self.x, 2), np.power(P, 2)))
        s22 = 1/nFreq * np.sum(np.multiply(np.power(self.x, 4), np.power(P, 2)))
        s = [[0, s01, s02], [0, s11, s12], [0, s12, s22]]

        return s

    def mle_ab(self, s, n):
        """
        Calculation of the pre-parameters a and b, according to the paper of Norrelyke

        Args:
            s (list of float): matrix with the S coefficients
            n (float): number of averaged power spectra (total data points divided by the block length)

        Returns:
            a, b (float): pre-parameters for the calculation of D and fc
        """

        a = ((1+1/n)/(s[0][2]*s[2][2]-s[1][2]*s[1][2])) * (s[0][1]*s[2][2]-s[1][1]*s[1][2])
        b = ((1+1/n)/(s[0][2]*s[2][2]-s[1][2]*s[1][2])) * (s[1][1]*s[0][2]-s[0][1]*s[1][2])
        return a, b

    def mle_parameters(self, a, b, n):
        """Calculate parameters from the factors of the MLE

        Args:
            a, b (float): pre-parameters for the calculation of D and fc
            n (float): number of averaged power spectra (total data points divided by the block length)

        Returns:
            D (float): diffusion constant in units of [V]
            fc (float): corner frequency in units of [Hz]

        """

        if a*b > 0:
            fc = np.sqrt(a/b)
        else:
            fc = 0
        D = (n * np.pi**2/(n+1)) / b

        return D, fc

    def mle_errors(self, D, fc, a, b, n):
        """Function to get the standard deviation of the parameters according to the paper of Norrelyke

        Args:
            f (np.array): array of the frequencies in units of [Hz]
            D (float): diffusion constant in units of [V]
            fc (float): corner frequency in units of [Hz]
            a, b (float): pre-parameters for the calculation of D and fc
            n (float): number of averaged power spectra (total data points divided by the block length)

        Returns:
            errosMle (np.array): with sigma(D) and sigma(fc)
        """

        s = self.mle_factors(self.yFit)
        sB = [[(n+1)/n*s[0][2], (n+1)/n*s[1][2]], [(n+1)/n*s[1][2], (n+1)/n*s[2][2]]]
        sError = 1/(len(self.x)*n)*(n+3)/n*np.linalg.inv(sB)

        sigmaFc = fc**2/4 * (sError[0][0]/a**2+sError[1][1]/b**2-2*sError[0][1]/(a*b))
        sigmaD = D**2*(sError[1][1]/b**2)
        errorsMle = [np.sqrt(sigmaD), np.sqrt(sigmaFc)]

        return errorsMle


class PsdFit():
    """
    Fit the PSD.
    """

    def __init__(self, container, fitCls=PsdFitLeastSquares, minF=5, maxF=3*10**3, residuals=True, **fitargs):
        """
        Constructor for PsdFit

        Args:
            container (:class:`tweezer.TweezerData`): data container
            fitCls (:class:`ixo.fit.Fit`): class to use for fitting, must implement the methods given in the
                                            reference class
            minF (float): only data points with frequencies above this limit are fitted
            maxF (float): only data points with frequencies below this limit are fitted
            residuals (bool): compute the residuals for the fit, they are added as columns to the PSD data in the
                              container structure
            startingValues (list): starting values for the fitting routine, optional
        """

        self.c = container
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
        Fit the PSD with the fitting class given in the constructor. There is no return value but the results are
        written back to the data container object. Also, the fitted curve is added to the PSD data.
        Note that what the value stored under ``PsdFitError`` in the data container's meta data can describe
        different things depending on the used fitting class.
        """

        # dataframe to hold result
        psdFit = self.c.psd[['f']][(self.c.psd['f'] >= self.minF) & (self.c.psd['f'] <= self.maxF)]

        for title, column in self.c.psd.iteritems():
            if not title.endswith('X') and not title.endswith('Y'):
                # only do psd columns, their data should end on 'X' or 'Y'
                continue

            # pick data for fitting based on given frequency limits
            data = self.c.psd[['f', title, title + 'Std']]
            data = data[(data['f'] >= self.minF) & (data['f'] <= self.maxF)]

            # create fit object and do the fit
            fitObj = self.fitCls(data['f'],
                                 data[title],
                                 fcn=self.lorentzian,
                                 std=data[title + 'Std'],
                                 container=self.c,
                                 **self.fitargs)
            res = fitObj.fit()

            # store results
            D = res[0]
            fc = res[1]
            self.c.meta.set(title, 'D', D)
            self.c.meta.set(title, 'fc', fc)
            self.c.meta.set(title, 'PsdFitError', list(fitObj.fitError))  # convert to list for conversion to JSON
            self.c.meta.set(title, 'r2', fitObj.rsquared())
            self.c.meta.set(title, 'chi2', fitObj.chisquared())
            self.c.meta.set(title, 'FitMinF', self.minF)
            self.c.meta.set(title, 'FitMaxF', self.maxF)

            # get stiffness and store it
            beadKey = self.c.meta.get_key(title, 'BeadDiameter')
            radius = self.c.meta[beadKey] / 2
            if self.c.units[beadKey] in ['um', 'µm']:
                radius *= 1000
            dist_calib = distance_calibration(D=D,
                                              radius=radius,
                                              viscosity=self.c.meta['viscosity'],
                                              T=self.c.meta['temperature'])
            stiffness = trap_stiffness(fc=fc,
                                       radius=radius,
                                       viscosity=self.c.meta['viscosity'])
            self.c.meta.set(title, 'k', stiffness)
            # TODO check if units are there for stiffness, distance_calibration and temperature!!!!!
            self.c.meta.set(title, 'beta', dist_calib)

            # append plotting data to psd only for fitting range
            # pick data for fitting based on given limits
            psdFit[title + 'Fit'] = self.lorentzian(psdFit['f'], D, fc)

            # compute residuals
            if self.residuals:
                psdFit[title + 'Residuals'], meanResidual = fitObj.residuals()
                self.c.meta.set(title, 'MeanResidualPsd', meanResidual)

        return psdFit

    @staticmethod
    def lorentzian(f, D, fc):
        """
        Lorentzian function

        Args:
            f (:class:`numpy.array`): frequency in units of [Hz]
            D (float): diffusion constant in units of [V]
            fc (float): corner frequency in units of [Hz]

        Returns:
            :class:`numpy.array`
        """

        return D / (np.pi ** 2 * (f ** 2 + fc ** 2))