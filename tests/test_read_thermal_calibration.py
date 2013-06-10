#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest
import sure
import datetime

from tweezer import path_to_sample_data
from tweezer.io import read_tweezer_power_spectrum

TS = path_to_sample_data('TC_TS')
PSD = path_to_sample_data('TC_PSD')


def test_read_tweezer_power_spectrum():
    psd = read_tweezer_power_spectrum(PSD)
    psd.date.should.equal(datetime.datetime(2013, 5, 19, 2, 34))
    psd.nSamples.should.equal(2**20) 
    psd.nBlocks.should.equal(128) 
    psd.sampleRate.should.equal(80000) 

    # units
    psd.units["yOffsetT1"].should.equal("V") 
    
    
    
    
    

# Testing the test
def main():
    print(TS)
    print(PSD)

if __name__ == '__main__':
    main()
