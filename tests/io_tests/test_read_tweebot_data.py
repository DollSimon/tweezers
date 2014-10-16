#!/usr/bin/env python
#-*- coding: utf-8 -*-

import datetime

import pytest

from tweezer.io import read_tweebot_data
from tweezer import path_to_sample_data
from tweezer.legacy.core.parsers import classify

# get example file
bot_file = path_to_sample_data('bot_data')

@pytest.fixture
def botData():
    """
    Data read from Tweebot datalog file.
    """
    data = read_tweebot_data(bot_file)
    return data


def test_file_identity():
    assert classify(bot_file) == 'BOT_DATA'


def test_type_of_returned_data(botData):
    assert isinstance(botData, 'pandas.core.frame.DataFrame')


def test_return_values(botData):
    # check results
    assert botData.units['timeStep'] == 's'
    assert botData.units['ccdPmCenterX'] == 'px'
    assert botData.units['laserDiodeTemp'] == 'C'
    assert botData.units['laserDiodeTemp'] == 'C'
    assert botData.units['laserDiodeHours'] == 'h'
    assert botData.units['laserDiodeCurrent'] == 'A'
    assert botData.units['andorAodCenterX'] == 'px'
    assert botData.units['andorAodCenterY'] == 'px'
    assert botData.units['andorAodRangeX'] == 'px'
    assert botData.units['andorAodRangeY'] == 'px'
    assert botData.units['ccdAodCenterX'] == 'px'
    assert botData.units['ccdAodCenterY'] == 'px'
    assert botData.units['ccdAodRangeX'] == 'px'
    assert botData.units['ccdAodRangeY'] == 'px'
    assert botData.units['andorPmCenterX'] == 'px'
    assert botData.units['andorPmCenterY'] == 'px'
    assert botData.units['andorPmRangeX'] == 'px'
    assert botData.units['andorPmRangeY'] == 'px'
    assert botData.units['ccdPmCenterX'] == 'px'
    assert botData.units['ccdPmCenterY'] == 'px'
    assert botData.units['ccdPmRangeX'] == 'px'
    assert botData.units['ccdPmRangeY'] == 'px'
    assert botData.units['andorPixelSizeX'] == 'nm'
    assert botData.units['andorPixelSizeY'] == 'nm'
    assert botData.units['ccdPixelSizeX'] == 'nm'
    assert botData.units['ccdPixelSizeY'] == 'nm'
    assert botData.units['aodDetectorOffsetX'] == 'V'
    assert botData.units['aodDetectorOffsetY'] == 'V'
    assert botData.units['aodStiffnessX'] == 'pN/nm'
    assert botData.units['aodStiffnessY'] == 'pN/nm'
    assert botData.units['aodDisplacementSensitivityX'] == 'V/nm'
    assert botData.units['aodDisplacementSensitivityY'] == 'V/nm'
    assert botData.units['pmDetectorOffsetX'] == 'V'
    assert botData.units['pmDetectorOffsetY'] == 'V'
    assert botData.units['pmStiffnessX'] == 'pN/nm'
    assert botData.units['pmStiffnessY'] == 'pN/nm'
    assert botData.units['pmDisplacementSensitivityX'] == 'V/nm'
    assert botData.units['pmDisplacementSensitivityY'] == 'V/nm'
    assert botData.units['aodBeadRadius'] == 'nm'
    assert botData.units['pmBeadRadius'] == 'nm'
    assert botData.units['samplingRate'] == 'Hz'
    assert botData.units['nSamples'] == 'int'
    assert botData.units['deltaTime'] == 's'

    assert botData.meta['laserDiodeTemp'] == 23.6300
    assert botData.meta['laserDiodeHours'] == 19306.1
    assert botData.meta['laserDiodeCurrent'] == 13.0000
    assert botData.meta['andorAodCenterX'] == 268.708
    assert botData.meta['andorAodCenterY'] == 265.323
    assert botData.meta['andorAodRangeX'] == 24.8333
    assert botData.meta['andorAodRangeY'] == 24.7083
    assert botData.meta['ccdAodCenterX'] == 298.188
    assert botData.meta['ccdAodCenterY'] == 291.125
    assert botData.meta['ccdAodRangeX'] == 93.7500
    assert botData.meta['ccdAodRangeY'] == 110.750
    assert botData.meta['andorPmCenterX'] == 272.906
    assert botData.meta['andorPmCenterY'] == 271.688
    assert botData.meta['andorPmRangeX'] == 14.3750
    assert botData.meta['andorPmRangeY'] == 9.25000
    assert botData.meta['ccdPmCenterX'] == 310.500
    assert botData.meta['ccdPmCenterY'] == 324.500
    assert botData.meta['ccdPmRangeX'] == 53.0000
    assert botData.meta['ccdPmRangeY'] == 42.5000
    assert botData.meta['andorPixelSizeX'] == 293.940
    assert botData.meta['andorPixelSizeY'] == 288.530
    assert botData.meta['ccdPixelSizeX'] == 74.1000
    assert botData.meta['ccdPixelSizeY'] == 61.6000
    assert botData.meta['aodDetectorOffsetX'] == -0.165608
    assert botData.meta['aodDetectorOffsetY'] == 0.725181
    assert botData.meta['aodStiffnessX'] == 0.166681
    assert botData.meta['aodStiffnessY'] == 0.163667
    assert botData.meta['aodDisplacementSensitivityX'] == 0.00102400
    assert botData.meta['aodDisplacementSensitivityY'] == 0.00108100
    assert botData.meta['pmDetectorOffsetX'] == -0.0493670
    assert botData.meta['pmDetectorOffsetY'] == 0.0642740
    assert botData.meta['pmStiffnessX'] == 0.194668
    assert botData.meta['pmStiffnessY'] == 0.158991
    assert botData.meta['pmDisplacementSensitivityX'] == 0.000937000
    assert botData.meta['pmDisplacementSensitivityY'] == 0.000821000
    assert botData.meta['aodBeadRadius'] == 1015
    assert botData.meta['pmBeadRadius'] == 1080
    assert botData.meta['samplingRate'] == 1000
    assert botData.meta['nSamples'] == 1
    assert botData.meta['deltaTime'] == 0.001


real_file = '/Users/jahnel/code/example_data/tweebot/datalog/18.Datalog.2013.02.19.23.09.24.datalog.txt'

@pytest.mark.skip
def test_real_file():
    df = read_tweebot_data(real_file)
    assert df.units['deltaTime'] == 's'
    assert df.date == datetime.datetime(2013, 2, 19, 23, 9, 24)
