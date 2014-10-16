import pytest

import pandas as pd

from numpy.testing import assert_allclose

try:
    from tweezer.legacy.statistics import fit_wlc
except ImportError as err:
    print('The tweezer package has not been correctly installed or updated.')
    raise err


@pytest.fixture
def data():
    data = pd.read_table('/Users/jahnel/code/example_data/dna_fitting_R.txt')
    return data


def test_fitting_wlc_dna_model_with_simulated_data(data):

    fitData = data[['extension', 'force']]

    fitResult = fit_wlc(fitData)

    assert_allclose(fitResult.L, 640, rtol=0.2)
    assert_allclose(fitResult.P, 50, rtol=0.2)
    assert_allclose(fitResult.S, 1200, rtol=0.2)

    wlcModel = fitResult.model
    wlcFit = fitResult.fit

    assert_allclose(wlcFit.params[0], 640, rtol=0.2)

    assert wlcModel == 'extension ~ 1 + np.sqrt(kBT/(force)) + force'
    assert wlcFit.rsquared > 0.9
