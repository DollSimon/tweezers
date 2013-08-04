#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import datetime

import unittest
import sure

from clint.textui import colored, puts, indent

try:
    from tweezer import path_to_sample_data
    from tweezer.io import read_tweezer_power_spectrum
except ImportError, err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')

TS = path_to_sample_data('TC_TS')
PSD = path_to_sample_data('TC_PSD')


class TestReadingThermalCalibrationData:

    @classmethod
    def setup_class(cls):
        cls.man_psd = os.path.expanduser('~/code/example_data/manual/thermal_calibration/PSD_4_c.txt')

    def test_read_tweebot_power_spectrum(self):
        psd = read_tweezer_power_spectrum(PSD)
        psd.date.should.equal(datetime.datetime(2013, 5, 19, 2, 34))
        psd.nSamples.should.equal(2**20) 
        psd.nBlocks.should.equal(128) 
        psd.samplingRate.should.equal(80000) 

        # units
        psd.units["pmDetectorOffsetY"].should.equal("V") 

        # values
        psd.pmStiffnessX.should.equal(0.116529)

        psd.aodDetectorOffsetY.should.equal(0.384392)
        # yOffsetT2.V:  0.384392

        psd.aodDetectorOffsetX.should.equal(-0.183561)
        # xOffsetT2.V: -0.183561

        psd.aodCornerFreqY.should.be(651.121403)
        # yCornerFreqT2.Hz 651.121403

        psd.aodCornerFreqX.should.be(787.229555)
        # xCornerFreqT2.Hz: 787.229555

        psd.aodStiffnessY.should.be(0.077116)
        # yStiffnessT2.pNperNm: 0.077116

        psd.aodStiffnessX.should.be(0.093236)
        # xStiffnessT2.pNperNm: 0.093236

        psd.aodDisplacementSensitivityY.should.be(0.000606)
        # yDistConversionT2.VperNm: 0.000606

        psd.aodDisplacementSensitivityX.should.be(0.000625)
        # xDistConversionT2.VperNm: 0.000625

        psd.pmDetectorOffsetY.should.equal(0.016076)
        # yOffsetT1.V:  0.016076

        psd.pmDetectorOffsetX.should.equal(-0.119340)
        # xOffsetT1.V: -0.119340

        psd.pmCornerFreqY.should.be(618.791988)
        # yCornerFreqT1.Hz 618.791988

        psd.pmCornerFreqX.should.be(911.026211)
        # xCornerFreqT1.Hz: 911.026211

        psd.pmStiffnessY.should.be(0.079150)
        # yStiffnessT1.pNperNm: 0.079150

        psd.pmStiffnessY.should.be(0.116529)
        # xStiffnessT1.pNperNm: 0.116529

        psd.pmDisplacementSensitivityY.should.be(0.000695)
        # yDistConversionT1.VperNm: 0.000695

        psd.pmDisplacementSensitivityX.should.be(0.000854)
        # xDistConversionT1.VperNm: 0.000854

        psd.pmBeadDiameter.should.be(2160)
        # diameterT1.um: 2.160000

        psd.aodBeadDiameter.should.be(2000)
        psd.aodBeadRadius.should.be(1000)
        # diameterT2.um: 2.000000

    def test_read_old_manual_power_spectrum(self):
        psd_file = self.__class__.man_psd
        psd = read_tweezer_power_spectrum(psd_file)
        
        # units
        psd.units["pmDetectorOffsetY"].should.equal("V") 

        # values
        psd.nBlocks.should.equal(128) 
        psd.nSamples.should.equal(2**20) 
        psd.samplingRate.should.equal(80000) 
        psd.date.should.equal(datetime.datetime(2013, 2, 22, 16, 21))

        psd.aodDetectorOffsetY.should.be(0.571595)
        psd.aodDetectorOffsetX.should.be(-0.074555)
        psd.aodCornerFreqY.should.be(131.916394)
        psd.aodCornerFreqX.should.be(190.906543)
        psd.aodStiffnessY.should.be(0.050094)
        psd.aodStiffnessX.should.be(0.072495)
        psd.aodDisplacementSensitivityY.should.be(0.000349)
        psd.aodDisplacementSensitivityX.should.be(0.000424)

        psd.pmDetectorOffsetY.should.be(0.091648)
        psd.pmDetectorOffsetX.should.be(-0.075828)
        psd.pmCornerFreqY.should.be(152.806556)
        psd.pmCornerFreqX.should.be(161.970405)
        psd.pmStiffnessY.should.be(0.058027)
        psd.pmStiffnessX.should.be(0.061506)
        psd.pmDisplacementSensitivityY.should.be(0.000367)
        psd.pmDisplacementSensitivityX.should.be(0.000384)

        psd.pmBeadDiameter.should.be(2000)
        psd.aodBeadDiameter.should.be(2000)

