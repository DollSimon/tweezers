import pytest

import pandas as pd

try:
    from tweezer.noise.allan import allan_var
except ImportError as err:
    print('The tweezer package has not been correctly installed or updated.')
    raise err

dataFile = "~/code/example_data/allanData.txt"


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


def test_essential_allan_variance_calculation(data, rResults):

    results = allan_var(data)

    assert isinstance(results, pd.core.frame.DataFrame)
    assert 'av' in results
    assert 'error' in results

    assert results == rResults
