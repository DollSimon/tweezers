import pytest

try:
    import simplejson as json
except ImportError:
    import json

from tweezer import path_to_sample_data
from tweezer.legacy.ixo2.json_ import calibration_to_json


@pytest.fixture
def calibAsJson():
    dataFile = path_to_sample_data('MAN_DATA')
    calibAsJson = calibration_to_json(dataFile)
    return calibAsJson


def test_calibration_can_be_transformed_to_json():
    dataFile = path_to_sample_data('MAN_DATA')
    calibAsJson = calibration_to_json(dataFile)

    assert calibAsJson is not None
    assert isinstance(calibAsJson, str)


def test_reading_data_back_to_dictionary(calibAsJSON):
    calibData = json.loads(calibAsJson)

    assert "metaData" in calibData
    assert "units" in calibData

