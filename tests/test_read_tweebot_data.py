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
    data = read_tweebot_data(bot_file)
    data.should.be.a('pandas.core.frame.DataFrame')

    # check results
    data.units['timeStep'].should.equal('s')
    data.units['ccdPmCenterX'].should.equal('px')

    data.meta['samplingRate'].should.equal(1000)
    data.meta['aodStiffnessX'].should.equal(0.166681)
    data.meta['andorPmRangeX'].should.be(14.3750)
    data.meta['andorAodCenterX'].should.be(268.708)
