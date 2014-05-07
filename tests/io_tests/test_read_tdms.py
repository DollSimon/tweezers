#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pytest

from tweezer import path_to_sample_data
from tweezer.io import read_tdms

tdmsFile = path_to_sample_data('bot_tdms')


@pytest.fixture
def tdmsData():
    data = read_tdms(tdmsFile)
    return data


def test_reading_tdms_file(tdmsData):
    assert len(tdmsData) == 9370

