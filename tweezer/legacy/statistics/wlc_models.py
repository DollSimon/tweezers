__doc__ = """\
Statistics and fitting routines related to polymer models
"""

from collections import namedtuple

from statsmodels.formula.api import ols
from tweezer.legacy.physics2 import thermal_energy


def fit_wlc(fitData):
    """
    Fits the extensible worm-like chain model to data

    :param fitData:
    """

    WLC_FIT = namedtuple("WLC_FIT", ["L", "P", "S", "model", "fit"])

    kBT = thermal_energy()
    wlcModel = 'extension ~ 1 + np.sqrt(kBT/(force)) + force'

    try:
        wlcFit = ols(formula=wlcModel, data=fitData).fit()
    except:
        raise BaseException("Can't fit the data like this... ;-((")

    contourLength = wlcFit.params[0]
    persistenceLength = 1 / (-2 * (wlcFit.params[1] / wlcFit.params[0])) ** 2
    stretchModulus = 1 / (wlcFit.params[2] / wlcFit.params[0])

    fitResults = WLC_FIT(contourLength, persistenceLength, stretchModulus, wlcModel, wlcFit)

    return fitResults