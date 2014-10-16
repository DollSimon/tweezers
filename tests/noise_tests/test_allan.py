import pytest

import numpy as np
import pandas as pd
from numpy.testing import assert_approx_equal

try:
    from tweezer import path_to_sample_data
    from tweezer.io import read_thermal_calibration
    from tweezer.legacy.noise.allan import allan_variance_r_port as allan_var
    from tweezer.legacy.noise.allan import allan_variance
except ImportError as err:
    print('The tweezer package has not been correctly installed or updated.')
    raise err

dataFile = "~/code/example_data/allanData.txt"


@pytest.fixture
def calibrationData():
    timeSeries = path_to_sample_data("TC_TS")
    data = read_thermal_calibration(timeSeries, frequency=80000)
    return data


@pytest.fixture
def data():
    data = pd.read_table('/Users/jahnel/code/example_data/allanData.txt', header=None, nrows=65536)
    times = pd.date_range(start='2000-1-1', periods=len(data), freq='10L')
    data.index = times
    data.columns = ["ts"]
    return data


@pytest.fixture
def rResults():
    results = pd.read_table("/Users/jahnel/code/example_data/allanResults_R.txt", sep="\t", index_col="time")
    return results


@pytest.mark.slow
def test_essential_allan_variance_calculation(data, rResults):

    print("len(data): {}".format(len(data)))

    results = allan_var(data, 100)

    assert isinstance(results, pd.core.frame.DataFrame)
    assert 'av' in results
    assert 'error' in results
    assert all(results.index == pd.Float64Index([0.01, 0.02, 0.04, 0.08, 0.16, 0.32, 0.64, 1.28, 2.56, 5.12, 10.24, 20.48, 40.96, 81.92, 163.84, 327.68], dtype='object'))

    assert all(results == rResults)


def test_faster_allan_variance_calculation(data, rResults):

    rate = 100
    testData = np.array(data.ix[:, 0])

    results = allan_variance(testData, rate)

    assert results is not None
    # assert results[0] == rResults.av.iloc[0]
    assert_approx_equal(results[0], rResults.av.iloc[0])


def test_allan_variance_on_real_data(calibrationData):

    rate = 80000
    testData = np.array(calibrationData.iloc[:, 0])

    results = allan_variance(testData, rate)

    assert results is not None


