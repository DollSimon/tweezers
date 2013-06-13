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
    data.units['laserDiodeTemp'].should.equal('C')
    data.units['laserDiodeTemp'].should.equal('C') 
    data.units['laserDiodeHours'].should.equal('h')
    data.units['laserDiodeCurrent'].should.equal('A')
    data.units['andorAodCenterX'].should.equal('px')
    data.units['andorAodCenterY'].should.equal('px')
    data.units['andorAodRangeX'].should.equal('px')
    data.units['andorAodRangeY'].should.equal('px')
    data.units['ccdAodCenterX'].should.equal('px')
    data.units['ccdAodCenterY'].should.equal('px')
    data.units['ccdAodRangeX'].should.equal('px')
    data.units['ccdAodRangeY'].should.equal('px')
    data.units['andorPmCenterX'].should.equal('px')
    data.units['andorPmCenterY'].should.equal('px')
    data.units['andorPmRangeX'].should.equal('px')
    data.units['andorPmRangeY'].should.equal('px')
    data.units['ccdPmCenterX'].should.equal('px')
    data.units['ccdPmCenterY'].should.equal('px')
    data.units['ccdPmRangeX'].should.equal('px')
    data.units['ccdPmRangeY'].should.equal('px')
    data.units['andorPixelSizeX'].should.equal('nm')
    data.units['andorPixelSizeY'].should.equal('nm')
    data.units['ccdPixelSizeX'].should.equal('nm')
    data.units['ccdPixelSizeY'].should.equal('nm')
    data.units['aodDetectorOffsetX'].should.equal('V')
    data.units['aodDetectorOffsetY'].should.equal('V')
    data.units['aodStiffnessX'].should.equal('pN/nm')
    data.units['aodStiffnessY'].should.equal('pN/nm')
    data.units['aodDistanceConversionX'].should.equal('V/nm')
    data.units['aodDistanceConversionY'].should.equal('V/nm')
    data.units['pmDetectorOffsetX'].should.equal('V')
    data.units['pmDetectorOffsetY'].should.equal('V')
    data.units['pmStiffnessX'].should.equal('pN/nm')
    data.units['pmStiffnessY'].should.equal('pN/nm')
    data.units['pmDistanceConversionX'].should.equal('V/nm')
    data.units['pmDistanceConversionY'].should.equal('V/nm')
    data.units['aodBeadRadius'].should.equal('nm')
    data.units['pmBeadRadius'].should.equal('nm')
    data.units['samplingRate'].should.equal('Hz')
    data.units['nSamples'].should.equal('int')
    data.units['deltaTime'].should.equal('s')

    data.meta['laserDiodeTemp'].should.equal(23.6300)
    data.meta['laserDiodeHours'].should.equal(19306.1)
    data.meta['laserDiodeCurrent'].should.equal(13.0000)
    data.meta['andorAodCenterX'].should.equal(268.708)
    data.meta['andorAodCenterY'].should.equal(265.323)
    data.meta['andorAodRangeX'].should.equal(24.8333)
    data.meta['andorAodRangeY'].should.equal(24.7083)
    data.meta['ccdAodCenterX'].should.equal(298.188)
    data.meta['ccdAodCenterY'].should.equal(291.125)
    data.meta['ccdAodRangeX'].should.equal(93.7500)
    data.meta['ccdAodRangeY'].should.equal(110.750)
    data.meta['andorPmCenterX'].should.equal(272.906)
    data.meta['andorPmCenterY'].should.equal(271.688)
    data.meta['andorPmRangeX'].should.equal(14.3750)
    data.meta['andorPmRangeY'].should.equal(9.25000)
    data.meta['ccdPmCenterX'].should.equal(310.500)
    data.meta['ccdPmCenterY'].should.equal(324.500)
    data.meta['ccdPmRangeX'].should.equal(53.0000)
    data.meta['ccdPmRangeY'].should.equal(42.5000)
    data.meta['andorPixelSizeX'].should.equal(293.940)
    data.meta['andorPixelSizeY'].should.equal(288.530)
    data.meta['ccdPixelSizeX'].should.equal(74.1000)
    data.meta['ccdPixelSizeY'].should.equal(61.6000)
    data.meta['aodDetectorOffsetX'].should.equal(-0.165608)
    data.meta['aodDetectorOffsetY'].should.equal(0.725181)
    data.meta['aodStiffnessX'].should.equal(0.166681)
    data.meta['aodStiffnessY'].should.equal(0.163667)
    data.meta['aodDistanceConversionX'].should.equal(0.00102400)
    data.meta['aodDistanceConversionY'].should.equal(0.00108100)
    data.meta['pmDetectorOffsetX'].should.equal(-0.0493670)
    data.meta['pmDetectorOffsetY'].should.equal(0.0642740)
    data.meta['pmStiffnessX'].should.equal(0.194668)
    data.meta['pmStiffnessY'].should.equal(0.158991)
    data.meta['pmDistanceConversionX'].should.equal(0.000937000)
    data.meta['pmDistanceConversionY'].should.equal(0.000821000)
    data.meta['aodBeadRadius'].should.equal(1015)
    data.meta['pmBeadRadius'].should.equal(1080)
    data.meta['samplingRate'].should.equal(1000)
    data.meta['nSamples'].should.equal(1)
    data.meta['deltaTime'].should.equal(0.001)
