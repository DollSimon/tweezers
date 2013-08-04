#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sure

import numpy as np

from tweezer.ixo.math import map_array_to_range

def test_map_array_to_default_range():
    X = np.array([-1.5, 4.3, 3, -4.3, -2, 0, 2.3])
    nX = map_array_to_range(X)
    nX[1].should.equal(1) 
    nX[3].should.equal(-1) 
    nX[5].should.equal(0)
    
