#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import datetime

import unittest
import sure

from collections import Counter

from clint.textui import colored, puts, indent

try:
    from tweezer.io import standardized_name_of, standardized_unit_of
except ImportError as err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')


@pytest.fixture\
def names():
    return ['xDistConversionT1.VperNm', 'yDistConversionT1.VperNm',
            'PM detector x offset', 'PM detector y offset', 'zOffsetT1.V',
            'PM trap stiffness x', 'PM trap stiffness y', 
            'PM trap distance conversion y', 'PM ANDOR center x',
            'AOD vertical OLS', 'AOD detector y offset']


def test_validity_of_keys(names):
    for name in names:
        assert isinstance(name, str)

def test_standardized_units(self):
    units = []
    for name in self.names:
        units.append(standardized_unit_of(name))

        # inside
        ('px').should.be.within(units)
        ('V').should.be.within(units)
        ('pN/nm').should.be.within(units)
        ('V/nm').should.be.within(units)

        # not inside
        ('s').shouldnot.be.within(units)
        ('nm').shouldnot.be.within(units)
        
        counts = Counter(units)
        counts['pN/nm'].should.equal(2) 
        
            

