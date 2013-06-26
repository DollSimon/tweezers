#!/usr/bin/env python
#-*- coding: utf-8 -*-

from itertools import chain

def read_image(file_name):
    pass

def read_andor_fits_stack(file_name):
    pass

def read_tweezer_avi(file_name):
    pass

def read_man_dist_cal_results(file_name, trap='pm'):
    """
    Reads distance calibration results
    
    :param file_name: (path) to the distance calibration file 
    :param trap: (str) designating the trap of interest, either 'pm' or 'aod'
    
    """
    pass


def read_distance_calibration_matrix(file_name):
    """
    Reads distance calibration matrix

    :param file_name: (path) to the distance calibration file 
    :param trap: (str) designating the trap of interest, either 'pm' or 'aod'
    """
    trap = 'pm' if 'pm' in file_name.lower() else 'aod'

    with open(file_name, 'r') as f:
        lines = f.readlines()
        lines = [l.strip().split('\t') for l in lines]

    data = [l for l in lines if len(l) == max(len(l) for l in lines)]
    setup = [l for l in lines if len(l) == min(len(l) for l in lines)]

    setup = list(chain.from_iterable(setup))

    # trap_steps = np.linspace(s)
    
    return lines, data, setup, trap

