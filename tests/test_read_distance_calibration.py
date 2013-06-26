#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sure

from tweezer import path_to_sample_data

from tweezer.dia.io import read_distance_calibration_matrix

def test_read_pm_distance_calibration_data():
    pm_dc_mat = path_to_sample_data('dist_cal_pm_mat')
    pm_data= read_distance_calibration_matrix(pm_dc_mat, trap='pm')
    pm_data.xmin.should.equal(1.0) 
    pm_data.steps.should.equal(20)
    
