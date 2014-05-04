#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pytest

# import datetime

from tweezer.io import read_tweebot_logs
from tweezer import path_to_sample_data
from tweezer.core.parsers import classify

# get example file
logFile = path_to_sample_data('bot_log')


@pytest.fixture
def logData():
    """
    Data read from Tweebot datalog file.
    """
    data = read_tweebot_logs(logFile)
    return data


def test_file_identity():
    assert classify(logFile) == 'BOT_LOG'


def test_type_of_returned_data(logData):
    assert isinstance(logData, 'pandas.core.frame.DataFrame')
    
    
def test_read_tweebot_log_opens_file(logData):
    assert len(logData.index) == 1042
