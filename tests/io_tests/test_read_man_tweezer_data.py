#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pytest
import datetime

from tweezer import path_to_sample_data
from tweezer.io import read_tweezer_txt

dataFile = path_to_sample_data('MAN_DATA')
badFile = path_to_sample_data('BAD_MAN_DATA')


@pytest.fixture
def goodData():
    data = read_tweezer_txt(dataFile)
    return data


@pytest.fixture
def badData():
    data = read_tweezer_txt(badFile)
    return data


def test_read_proper_man_data_file(goodData):
    assert goodData.date == datetime.datetime(2013, 3, 14, 19, 5)
    assert goodData.units['FBy'] == 'V'
    assert goodData.meta['recordingRate'] == 1000
    assert goodData.units['recordingRate'] == 'Hz'
    assert goodData.meta['timeStep'] == 0.001


def test_read_corrupted_man_data_file(badData):
    assert badData.date == datetime.datetime(2013, 6, 7, 12, 48)
    assert badData.meta['duration'] == 48
    assert badData.meta['timeStep'] == 0.001


    


