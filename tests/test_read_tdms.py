#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sure

from tweezer import path_to_sample_data
from tweezer.io import read_tdms

TDMS = path_to_sample_data('bot_tdms')

def test_reading_tdms_file():
    data = read_tdms(TDMS)
    len(data).should.be(9370)


