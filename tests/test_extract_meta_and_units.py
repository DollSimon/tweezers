#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sure

from tweezer.io import extract_meta_and_units
import pandas as pd

man_comments = [
    'Date of Experiment: 3/14/2013',
    'measurement starttime: 7:05 PM',
    'Laser Diode Status', 'Laser Diode Operating Hours (h): 0.000000',
    'Laser Diode Current (A): 0.000000', 'results thermal calibration:',
    'AOD detector vertical offset:  0.395940',
    'AOD detector horizontal offset: -0.107869',
    'AOD vertical trap stiffness (pN/nm): 0.065548',
    'AOD horizontal trap stiffness (pN/nm): 0.082585',
    'AOD vertical OLS (V/nm): 0.000433', 'AOD horizontal OLS (V/nm): 0.000484',
    'PM detector vertical offset:  0.022877',
    'PM detector horizontal offset: -0.117831',
    'PM vertical trap stiffness (pN/nm): 0.074521',
    'PM horizontal trap stiffness (pN/nm): 0.084382',
    'PM vertical OLS (V/nm): 0.000459',
    'PM horizontal OLS (V/nm): 0.000498',
    'PM bead diameter (um): 2.000000',
    'AOD bead diameter (um): 2.000000',
    'Viscosity (pN s / nm^2): 3.500000E-9',
    'sample rate (Hz): 10000',
    'number of samples: 10',
    'rate of while-loop(Hz):  1000',
    'dt (s): 0.00100',
    'data averaged to while-loop: FALSE',
    'start of measurement (iteration) : 2161878',
    'end of measurement (iteration) : 2170113',
    'duration of measurement(s): 8',
    'errors: 0\t0\t0\t0\t0']

dateOfExperiment = pd.to_datetime('3/14/2013 7:05 PM')


def test_extracting_man_comments():
    C = extract_meta_and_units(man_comments)

    C.should.have.property("units")
    C.should.have.property("metadata")

    C.units.should.be.a('dict')
    C.metadata.should.be.a('dict')

    # testing units
    C.units['duration'].should.equal('s')
    C.units['viscosity'].should.equal('pN s / nm^2')

    C.units['aodDetectorOffsetX'].should.equal('V')
    C.units['aodDetectorOffsetY'].should.equal('V')
    C.units['pmDetectorOffsetX'].should.equal('V')
    C.units['pmDetectorOffsetY'].should.equal('V')

    C.units['pmStiffnessX'].should.equal('pN/nm')
    C.units['pmStiffnessY'].should.equal('pN/nm')
    C.units['aodStiffnessX'].should.equal('pN/nm')
    C.units['aodStiffnessY'].should.equal('pN/nm')

    C.units['pmDistanceConversionX'].should.equal('V/nm')
    C.units['pmDistanceConversionY'].should.equal('V/nm')
    C.units['aodDistanceConversionX'].should.equal('V/nm')
    C.units['aodDistanceConversionY'].should.equal('V/nm')

    C.units['pmDisplacementSensitivityX'].should.equal('V/nm')
    C.units['pmDisplacementSensitivityY'].should.equal('V/nm')
    C.units['aodDisplacementSensitivityX'].should.equal('V/nm')
    C.units['aodDisplacementSensitivityY'].should.equal('V/nm')

    C.units['aodBeadDiameter'].should.equal('nm')
    C.units['pmBeadDiameter'].should.equal('nm')
    C.units['pmBeadRadius'].should.equal('nm')
    C.units['aodBeadRadius'].should.equal('nm')

    # testing naming in units dict
    C.units.should.have.key("duration")
    C.units.should.have.key("viscosity")
    C.units.should.have.key("timeStep")
    C.units.should.have.key("laserDiodeHours")
    C.units.should.have.key("laserDiodeCurrent")
    C.units.should.have.key("laserDiodeTemp")
    C.units.should.have.key("aodDetectorOffsetX")

    # testing values in meta
    C.metadata['aodBeadRadius'].should.equal(1000)
    C.metadata['pmBeadRadius'].should.equal(1000)

    C.metadata['pmBeadDiameter'].should.equal(2000)
    C.metadata['aodBeadDiameter'].should.equal(2000)

    C.metadata['pmStiffnessX'].should.equal(0.084382)
    C.metadata['pmStiffnessY'].should.equal(0.074521)
    C.metadata['aodStiffnessX'].should.equal(0.082585)
    C.metadata['aodStiffnessY'].should.equal(0.065548)

    C.metadata['pmDetectorOffsetX'].should.equal(-0.117831)
    C.metadata['pmDetectorOffsetY'].should.equal(0.022877)

    C.metadata['hasErrors'].should.equal(False)
    C.metadata['errors'].should.equal([0, 0, 0, 0, 0])

    C.metadata['pmDisplacementSensitivityX'].should.equal(0.000498)

    C.metadata['date'].should.equal(dateOfExperiment.to_datetime())
