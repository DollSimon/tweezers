from .decorators import lazy
from scipy.optimize import curve_fit
import numpy as np


class Fit():
    """
    Basic class for fitting.

    Attributes:
        coef:   computed fitting parameters
        yFit:   y values of fitted curve
    """
    
    def __init__(self, x, y, fcn=None, std=None, **kwargs):
        """
        Constructor for Fit, also performs the fit
        
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
    def coef(self):
        """
        Attribute to hold the computed fitting parameters.
        """

        return self.fit()

    @lazy
    def yFit(self):
        """
        Attribute to hold the y values of the fitted curve. Evaluated lazily.

        Returns:
            :class:`list` of :class:`float`, depending on the input
        """

        fit = self.fcn(self.x, *self.coef)
        return fit
        
    def rsquared(self):
        """
        R^2 value: :math:`R^2 = ...`
            formula source: http://en.wikipedia.org/wiki/Coefficient_of_determination

        Returns:
            :class:`float`
        """

        ssRes = np.sum((self.y - self.yFit)**2)
        ssTot = np.sum((self.y - np.mean(self.y))**2)
        return 1 - ssRes / ssTot

    def residuals(self):
        """
        Compute the residuals of the fit.

        Returns:
            :class:`numpy.ndarray` and :class:`float`
        """
        #TODO: check if OK

        residuals = (self.y - self.yFit) / self.yFit
        meanResidual = np.sum(residuals) / len(self.yFit)
        return residuals, meanResidual

    def chisquared(self):
        """
        Compute chi squared of the fit.

        Returns:
            :class:`float`
        """
        # TODO: check if OK

        if self.std is None or not any(self.std):
            raise AttributeError('No standard deviation data given for χ² computation.')

        chi2 = np.sum((self.y - self.yFit)**2 / self.std**2) / len(self.x)
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
                             sigma=std,
                             absolute_sigma=True,
                             **self.kwargs)
        # one standard deviation errors of the fitting parameters, only makes sense with weighted data points
        self.fitError = np.sqrt(np.diag(cov))

        return res


class PolyFit(Fit):
    """
    Perform a least squares fit of a polynoimal.

    Attributes:
        poly (:class:`numpy.polynomial.polynomial.Polynomial`): polynomial instance
        coef (:class:`numpy.ndarray`):  polynomial coefficients
        yFit (:class:`numpy.ndarray`):  y values of fitted curve
    """

    def __init__(self, x, y, order, **kwargs):
        """
        Constructor for PolyFit

        Args:
            x, y, order, kwargs
        """

        super().__init__(x, y, **kwargs)
        self.order = order

    def __call__(self, arg):
        """
        Evaluate the polynomial at the given position.
        """

        return self.poly(arg)

    def fit(self):
        """
        Do the fit. Returns only the fitted parameters, everything else is stored in class attributes. The standard
        deviation of the datapoints ist used for the weighting.

        Returns:
            :class:`numpy.ndarray` of parameters as determined by the fit.
        """

        mi = min(self.x)
        ma = max(self.x)
        #TODO: check for fitError
        poly = np.polynomial.Polynomial.fit(self.x, self.y, deg=self.order, w=self.std,
                                            domain=[mi, ma], window=[mi, ma])

        return poly

    @lazy
    def poly(self):
        """
        Get the `Polynomial` instance.

        Returns:
            :class:`numpy.polynomial.polynomial.Polynomial`
        """

        return self.fit()

    @lazy
    def coef(self):
        """
        Get the polynomial coefficients, see :attr:`numpy.polynomial.polynomial.Polynomial.coef`.

        Returns:
            :class:`numpy.ndarray`
        """

        return self.poly.coef

    @lazy
    def yFit(self):
        """
        Attribute to hold the y values of the fitted curve. Evaluated lazily.

        Returns:
            :class:`numpy.ndarray`
        """

        return self.poly(self.x)

    def linspace(self):
        """
        Return x, y values at equally spaced points in domain
        (see :meth:`numpy.polynomial.polynomial.Polynomial.linspace`).

        Returns:
            :class:`numpy.ndarray` with x, y
        """

        return self.poly.linspace()




