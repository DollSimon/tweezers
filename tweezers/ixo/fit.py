from .decorators import lazy
from scipy.optimize import curve_fit
import numpy as np


class Fit():
    """
    Basic class for fitting.
    """
    
    def __init__(self, x, y, fcn=None, std=None, **kwargs):
        """
        Constructor for Fit
        
        Args:
            x (:class:`list` of :class:`float`): x values
            y (:class:`list` of :class:`float`): y values
            fcn (function): function that is fitted to the data
            std (:class:`list` of :class:`float`): standard deviation of each data point, used for weighted fit and
                                                   chi squared calculation
            
        """

        self.x = x
        self.y = y
        self.fcn = fcn
        self.std = std
        self.kwargs = kwargs
        self.fitError = []

    @lazy
    def fitResult(self):
        """
        Attribute to hold the computed fitting parameters.
        """

        return self.fit()

    @lazy
    def fitY(self):
        """
        Attribute to hold the y values of the fitted curve. Evaluated lazily.

        Returns:
            :class:`list` of :class:`float`, depending on the input

        """

        fit = self.fcn(self.x, *self.fitResult)
        return fit
        
    def rsquared(self):
        """
        R^2 value: :math:`R^2 = ...`
            formula source: http://en.wikipedia.org/wiki/Coefficient_of_determination

        Returns:
            :class:`float`
        """

        ssRes = np.sum((self.y - self.fcn(self.x, *self.fitResult))**2)
        ssTot = np.sum((self.y - np.mean(self.y))**2)
        return 1 - ssRes / ssTot

    def residuals(self):
        """
        Compute the residuals of the fit.

        Returns:
            :numpy:`np.array` and :class:`float`
        """

        residuals = (self.y - self.fitY) / self.fitY
        meanResidual = np.sum(residuals) / len(self.fitY)
        return residuals, meanResidual

    def chisquared(self):
        """
        Compute chi squared of the fit.

        Returns:
            :class:`float`
        """

        if self.std is None or not any(self.std):
            raise AttributeError('No standard deviation data given for χ² computation.')

        chi2 = np.sum((self.y - self.fitY)**2 / self.std**2) / len(self.x)
        return chi2


class LeastSquaresFit(Fit):
    """
    Perform a least squares fit.
    """

    def __init__(self, *args, weighted=False, **kwargs):
        """
        Constructor

        Args:
            weighted (bool): Should the fit be weighted? This uses the standard deviation given with the data (same
                             as used for chi squared calculation).
        """

        # call parent constructor with all other arguments
        super().__init__(*args, **kwargs)
        # store weighted option
        self.weighted = weighted

    def fit(self):
        """
        Do the fit. Returns only the fitted parameters, everything else is stored in class attributes. The standard
        deviation of the datapoints ist used for the weighting.

        Returns:
            :class:`list` of parameters as determined by the fit.
        """

        # check for weighted option
        if self.weighted:
            std = self.std
        else:
            std = None

        # perform fit
        res, cov = curve_fit(self.fcn, self.x, self.y,
                                p0=[1, 20],
                                sigma=std,
                                absolute_sigma=True,
                                **self.kwargs)
        # one standard deviation errors of the fitting parameters, only makes sense with weighted data points
        self.fitError = np.sqrt(np.diag(cov))

        return res
