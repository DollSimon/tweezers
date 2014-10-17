import math

from ixo.fit import LeastSquaresFit
from scipy.signal import welch
import pandas as pd
from physics.tweezers import trap_stiffness


class PsdComputation():
    """
    Object to compute a PSD using Welch's method (:func:`scipy.signal.welch`).
    """

    def __init__(self, container, blockLength=2**13, nBlocks=None):
        """
        Constructor for PsdAnalysis

        Args:
            container (:class:`tweezer.TweezerData`): data container
            blockLength (float): number of data points per block (default: 2**13)
            nBlocks (int): The number of blocks determines the overlap between them. If set to ``None``, the number
                           is computed such that the overlap is 0.
        """

        self.c = container
        self.blockLength = blockLength
        self.nBlocks = nBlocks

    def psd(self):
        """
        Compute the PSDs for all axes in the data object. The units of the PSD are directly stored in the data
        container object.

        Returns:
            :class:`pandas.DataFrame`
        """

        # get nBlocks if set to 'None'
        # this corresponds to no overlap
        if not self.nBlocks:
            self.nBlocks = len(self.c.ts.ix[:, 0]) / self.blockLength

        psd = pd.DataFrame()
        for title, column in self.c.ts.items():
            fRaw, psdRaw = welch(column,
                                 fs=self.c.meta['samplingRateTs'],
                                 nperseg=self.blockLength,
                                 noverlap=self.overlap(column))

            # store psd, overwrites 'f' but it should be the same for all the axes so no problem here
            psd['f'] = fRaw
            # get rid of the 'diff' at the end of the title strings, should be there by convention
            titleNew = title.split('diff')[0]
            self.c.units[titleNew] = self.c.units[title] + '² / Hz'
            psd[titleNew] = psdRaw

        return psd

    def overlap(self, data):
        """
        Calculate window overlap from length of each window (block), their number and the total number of data
        points. The overlap is given in number of datapoints.

        Returns:
            :class:`int`
        """

        return self.blockLength - len(data) / self.nBlocks


class PsdFit():
    """
    Fit the PSD.
    """

    def __init__(self, container, fitCls=LeastSquaresFit):
        """
        Constructor for PsdFit

        Args:
            container (:class:`tweezer.TweezerData`): data container
            fitCls (:class:`ixo.fit.Fit`): class to use for fitting, must implement the methods given in the
                                            reference class
        """

        self.c = container
        # fit class to use
        self.fitCls = fitCls

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
            if title == 'f' or title.startswith('fit'):
                # skip frequency and possibly present 'fit...' columns
                continue
            # create fit object and do the fit
            self.fitObj[title] = self.fitCls(self.c.psd['f'], column, self.lorentzian)
            res = self.fitObj[title].fit()
            # store results
            self.D[title] = res[0]
            self.fc[title] = res[1]
            # convert std from numpy array to list, this is necessary to keep the MetaDict serializable as JSON-string
            self.std[title] = list(res[2])
            self.r2[title] = res[3]

        # update values in data structure
        for title, D in self.D.items():
            # update metadata
            self.c.meta.set(title, 'D', D)
            self.c.meta.set(title, 'fc', self.fc[title])
            self.c.meta.set(title, 'r2', self.r2[title])
            self.c.meta.set(title, 'PsdFitStd', self.std[title])

            # get stiffness and store it
            beadKey = self.c.meta.get_key(title, 'BeadDiameter')
            radius = self.c.meta[beadKey] / 2
            if self.c.units[beadKey] in ['um', 'µm']:
                radius *= 1000
            stiffness = trap_stiffness(fc=self.fc[title],
                                       radius=radius,
                                       viscosity=self.c.meta['viscosity'])
            self.c.meta.set(title, 'k', stiffness)

            # append plotting data to psd
            self.c.psd['fit' + title] = self.lorentzian(self.c.psd['f'], D, self.fc[title])

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