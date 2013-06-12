#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sure
import datetime

from tweezer import path_to_sample_data
from tweezer.io import read_tweezer_txt

data_file = path_to_sample_data('MAN_DATA')
bad_file = path_to_sample_data('BAD_MAN_DATA')

def test_read_proper_man_data_file():
    # read file
    good = read_tweezer_txt(data_file)

    # check results
    good.date.should.equal(datetime.datetime(2013, 3, 14, 19, 5)) 
    good.units['FBy'].should.equal('V')

    good.meta['recordingRate'].should.equal(1000)
    good.units['recordingRate'].should.equal('Hz')


def test_read_corrupted_man_data_file():
    # read file
    bad = read_tweezer_txt(bad_file)

    # check results
    bad.date.should.equal(datetime.datetime(2013, 6, 7, 12, 48))
    bad.meta['duration'].should.equal(48)
    

    


