#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pytest

from tweezer.io import extract_meta_and_units
import pandas as pd

manualComments = [
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


def test_extracting_manual_comments():
    C = extract_meta_and_units(manualComments)

    assert hasattr(C, 'units')
    assert hasattr(C, 'metadata')

    assert isinstance(C.units, dict)
    assert isinstance(C.metadata, dict)

    # testing units
    assert C.units['duration'] == 's'
    assert C.units['viscosity'] == 'pN s / nm^2'

    assert C.units['aodDetectorOffsetX'] == 'V'
    assert C.units['aodDetectorOffsetY'] == 'V'
    assert C.units['pmDetectorOffsetX'] == 'V'
    assert C.units['pmDetectorOffsetY'] == 'V'

    assert C.units['pmStiffnessX'] == 'pN/nm'
    assert C.units['pmStiffnessY'] == 'pN/nm'
    assert C.units['aodStiffnessX'] == 'pN/nm'
    assert C.units['aodStiffnessY'] == 'pN/nm'

    assert C.units['pmDistanceConversionX'] == 'V/nm'
    assert C.units['pmDistanceConversionY'] == 'V/nm'
    assert C.units['aodDistanceConversionX'] == 'V/nm'
    assert C.units['aodDistanceConversionY'] == 'V/nm'

    assert C.units['pmDisplacementSensitivityX'] == 'V/nm'
    assert C.units['pmDisplacementSensitivityY'] == 'V/nm'
    assert C.units['aodDisplacementSensitivityX'] == 'V/nm'
    assert C.units['aodDisplacementSensitivityY'] == 'V/nm'

    assert C.units['aodBeadDiameter'] == 'nm'
    assert C.units['pmBeadDiameter'] == 'nm'
    assert C.units['pmBeadRadius'] == 'nm'
    assert C.units['aodBeadRadius'] == 'nm'

    # testing naming in units dict
    assert "duration" in C.units
    assert "viscosity" in C.units
    assert "timeStep" in C.units
    assert "laserDiodeHours" in C.units
    assert "laserDiodeCurrent" in C.units
    assert "laserDiodeTemp" in C.units
    assert "aodDetectorOffsetX" in C.units

    # testing values in meta
    assert C.metadata['aodBeadRadius'] == 1000
    assert C.metadata['pmBeadRadius'] == 1000

    assert C.metadata['pmBeadDiameter'] == 2000
    assert C.metadata['aodBeadDiameter'] == 2000

    assert C.metadata['pmStiffnessX'] == 0.084382
    assert C.metadata['pmStiffnessY'] == 0.074521
    assert C.metadata['aodStiffnessX'] == 0.082585
    assert C.metadata['aodStiffnessY'] == 0.065548

    assert C.metadata['pmDetectorOffsetX'] == -0.117831
    assert C.metadata['pmDetectorOffsetY'] == 0.022877

    assert C.metadata['hasErrors'] == False
    assert C.metadata['errors'] == [0, 0, 0, 0, 0]

    assert C.metadata['pmDisplacementSensitivityX'] == 0.000498

    assert C.metadata['date'] == dateOfExperiment.to_datetime()
