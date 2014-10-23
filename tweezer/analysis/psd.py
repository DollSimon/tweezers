import math

from ixo.fit import LeastSquaresFit
from scipy.signal import welch
import pandas as pd
from physics.tweezers import trap_stiffness


class PsdComputation():
    """
    Object to compute a PSD using Welch's method (:func:`scipy.signal.welch`).
    """

    def __init__(self, container, blockLength=2**13, overlap=None, nBlocks=None):
        """
        Constructor for PsdAnalysis

        Args:
            container (:class:`tweezer.TweezerData`): data container
            blockLength (float): number of data points per block (default: 2**13)
            nBlocks (int): The number of blocks determines the overlap between them. If set to ``None``, the number
                           is computed such that the overlap is 0.
        """

        self.c = container
        self.blockLength = int(blockLength)
        if overlap:
            self.overlap = int(overlap)
        else:
            self.overlap = overlap
        self.nBlocks = nBlocks

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
            fRaw, psdRaw = welch(column,
                                 fs=self.c.meta['samplingRateTs'],
                                 nperseg=self.blockLength,
                                 noverlap=self.overlap)

            # store psd, overwrites 'f' but it should be the same for all the axes so no problem here
            psd['f'] = fRaw
            # get rid of the 'diff' at the end of the title strings, should be there by convention
            titleNew = title.split('Diff')[0]
            self.c.units[titleNew] = self.c.units[title] + '² / Hz'
            psd[titleNew] = psdRaw
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


class PsdFit():
    """
    Fit the PSD.
    """

    def __init__(self, container, fitCls=LeastSquaresFit, minF=5, maxF=3*10**3, residuals=True):
        """
        Constructor for PsdFit

        Args:
            container (:class:`tweezer.TweezerData`): data container
            fitCls (:class:`ixo.fit.Fit`): class to use for fitting, must implement the methods given in the
                                            reference class
            minF (float): only data points with frequencies above this limit are fitted
            maxF (float): only data points with frequencies below this limit are fitted
            r (bool): compute the residuals for the fit, they are added as columns to the PSD data in the container
                      structure
        """

        self.c = container
        # fit class to use
        self.fitCls = fitCls
        # fit limits
        self.minF = minF
        self.maxF = maxF
        self.residuals = residuals

        # hold fit results when required
        self.fitObj = {}
        self.D = {}
        self.fc = {}
        self.r2 = {}
        self.std = {}

    def fit(self):
        """
        Fit the PSD with the fitting class given in the constructor. There is no return value but the results are
        written back to the data container object. Also, the fitted curve is added to the PSD data.
        """

        for title, column in self.c.psd.iteritems():
            if title == 'f' or title.endswith('fit'):
                # skip frequency and possibly present 'fit...' columns
                continue

            # pick data for fitting based on given limits
            data = self.c.psd[['f', title]]
            data = data[(data['f'] >= self.minF) & (data['f'] <= self.maxF)]

            # create fit object and do the fit
            self.fitObj[title] = self.fitCls(data['f'], data[title], self.lorentzian)
            res = self.fitObj[title].fit()
            # store results
            self.D[title] = res[0]
            self.fc[title] = res[1]
            # convert std from numpy array to list, this is necessary to keep the MetaDict serializable as JSON-string
            self.std[title] = list(res[2])
            self.r2[title] = res[3]

        psdFit = self.c.psd[['f']][(self.c.psd['f'] >= self.minF) & (self.c.psd['f'] <= self.maxF)]
        # update values in data structure
        for title, D in self.D.items():
            # update metadata
            self.c.meta.set(title, 'D', D)
            self.c.meta.set(title, 'fc', self.fc[title])
            self.c.meta.set(title, 'r2', self.r2[title])
            self.c.meta.set(title, 'PsdFitStd', self.std[title])
            self.c.meta.set(title, 'FitMinF', self.minF)
            self.c.meta.set(title, 'FitMaxF', self.maxF)

            # get stiffness and store it
            beadKey = self.c.meta.get_key(title, 'BeadDiameter')
            radius = self.c.meta[beadKey] / 2
            if self.c.units[beadKey] in ['um', 'µm']:
                radius *= 1000
            stiffness = trap_stiffness(fc=self.fc[title],
                                       radius=radius,
                                       viscosity=self.c.meta['viscosity'])
            self.c.meta.set(title, 'k', stiffness)

            # append plotting data to psd only for fitting range
            # pick data for fitting based on given limits
            psdFit[title + 'Fit'] = self.lorentzian(psdFit['f'], D, self.fc[title])

            # compute residuals
            if self.residuals:
                psdFit[title + 'Residuals'], meanResidual = self.fitObj[title].residuals()
                self.c.meta.set(title, 'MeanResidualPsd')

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

        return D / (math.pi ** 2 * (f ** 2 + fc ** 2))