#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pytest

import os
import datetime

from clint.textui import colored, puts, indent

try:
    from tweezer import path_to_sample_data
    from tweezer.io import read_tweezer_power_spectrum
except ImportError as err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.'))
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err)))
        puts('')

botTimeSeriesFile = path_to_sample_data('TC_TS')
botPsdFile = path_to_sample_data('TC_PSD')


@pytest.fixture
def manPowerSpectrum():
    manPsdFile = os.path.expanduser('~/code/example_data/manual/thermal_calibration/PSD_4_c.txt')
    data = read_tweezer_power_spectrum(manPsdFile)
    return data


@pytest.fixture
def botPowerSpectrum():
    data = read_tweezer_power_spectrum(botPsdFile)
    return data


def test_man_psd_file_could_be_found(manPowerSpectrum):
    assert manPowerSpectrum is not None


def test_bot_psd_file_could_be_found(botPowerSpectrum):
    assert botPowerSpectrum is not None


def test_read_tweebot_power_spectrum(botPowerSpectrum):
    assert botPowerSpectrum.date == datetime.datetime(2013, 5, 19, 2, 34)
    assert botPowerSpectrum.nSamples == 2 ** 20
    assert botPowerSpectrum.nBlocks == 128
    assert botPowerSpectrum.samplingRate == 80000

    # unitts
    assert botPowerSpectrum.units["pmDetectorOffsetY"] == "V"

    # values
    # yOffsetT2.V:  0.384392
    # xOffsetT2.V: -0.183561
    # yCornerFreqT2.Hz 651.121403
    # xCornerFreqT2.Hz: 787.229555
    # yStiffnessT2.pNperNm: 0.077116
    # xStiffnessT2.pNperNm: 0.093236
    # yDistConversionT2.VperNm: 0.000606
    # xDistConversionT2.VperNm: 0.000625
    # yOffsetT1.V:  0.016076
    # xOffsetT1.V: -0.119340
    # yCornerFreqT1.Hz 618.791988
    # xCornerFreqT1.Hz: 911.026211
    # yStiffnessT1.pNperNm: 0.079150
    # xStiffnessT1.pNperNm: 0.116529
    # yDistConversionT1.VperNm: 0.000695
    # xDistConversionT1.VperNm: 0.000854
    # diameterT1.um: 2.160000
    # diameterT2.um: 2.000000
    assert botPowerSpectrum.pmStiffnessX == 0.116529
    assert botPowerSpectrum.aodDetectorOffsetY == 0.384392
    assert botPowerSpectrum.aodDetectorOffsetX == -0.183561
    assert botPowerSpectrum.aodCornerFreqY == 651.121403
    assert botPowerSpectrum.aodCornerFreqX == 787.229555
    assert botPowerSpectrum.aodStiffnessY == 0.077116
    assert botPowerSpectrum.aodStiffnessX == 0.093236
    assert botPowerSpectrum.aodDisplacementSensitivityY == 0.000606
    assert botPowerSpectrum.aodDisplacementSensitivityX == 0.000625
    assert botPowerSpectrum.pmDetectorOffsetY == 0.016076
    assert botPowerSpectrum.pmDetectorOffsetX == -0.119340
    assert botPowerSpectrum.pmCornerFreqY == 618.791988
    assert botPowerSpectrum.pmCornerFreqX == 911.026211
    assert botPowerSpectrum.pmStiffnessY == 0.079150
    assert botPowerSpectrum.pmStiffnessX == 0.116529
    assert botPowerSpectrum.pmDisplacementSensitivityY == 0.000695
    assert botPowerSpectrum.pmDisplacementSensitivityX == 0.000854
    assert botPowerSpectrum.pmBeadDiameter == 2160
    assert botPowerSpectrum.aodBeadDiameter == 2000
    assert botPowerSpectrum.aodBeadRadius == 1000


def test_read_old_manual_power_spectrum(manPowerSpectrum):
    # units
    assert manPowerSpectrum.units["pmDetectorOffsetY"] == "V"

    # values
    assert manPowerSpectrum.nBlocks == 128
    assert manPowerSpectrum.nSamples == 2 ** 20
    assert manPowerSpectrum.samplingRate == 80000
    assert manPowerSpectrum.date == datetime.datetime(2013, 2, 22, 16, 21)

    assert manPowerSpectrum.aodDetectorOffsetY == 0.571595
    assert manPowerSpectrum.aodDetectorOffsetX == -0.074555
    assert manPowerSpectrum.aodCornerFreqY == 131.916394
    assert manPowerSpectrum.aodCornerFreqX == 190.906543
    assert manPowerSpectrum.aodStiffnessY == 0.050094
    assert manPowerSpectrum.aodStiffnessX == 0.072495
    assert manPowerSpectrum.aodDisplacementSensitivityY == 0.000349
    assert manPowerSpectrum.aodDisplacementSensitivityX == 0.000424

    assert manPowerSpectrum.pmDetectorOffsetY == 0.091648
    assert manPowerSpectrum.pmDetectorOffsetX == -0.075828
    assert manPowerSpectrum.pmCornerFreqY == 152.806556
    assert manPowerSpectrum.pmCornerFreqX == 161.970405
    assert manPowerSpectrum.pmStiffnessY == 0.058027
    assert manPowerSpectrum.pmStiffnessX == 0.061506
    assert manPowerSpectrum.pmDisplacementSensitivityY == 0.000367
    assert manPowerSpectrum.pmDisplacementSensitivityX == 0.000384

    assert manPowerSpectrum.pmBeadDiameter == 2000
    assert manPowerSpectrum.aodBeadDiameter == 2000

