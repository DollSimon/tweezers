#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import unittest
import sure
import nose
from nose.tools import with_setup
import pytest

from tweezer.io import read_tweebot_data_header, read_tweebot_data
from tweezer import path_to_sample_data
from tweezer.core.parsers import classify

# get example file
bot_file = path_to_sample_data('bot_data')

def test_file_identity():
    classify(bot_file).should.equal('BOT_DATA') 
    

def test_return_values():
    df, cal = read_tweebot_data(bot_file)
    df.should.be.a('pandas.core.frame.DataFrame')
    cal.should.be.a('pandas.core.frame.DataFrame')
    

def test_clean_naming():
    cols, calib, header = read_tweebot_data_header(bot_file)
