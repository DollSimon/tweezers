#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Classes and Functions used for handling various data input and output tasks.
"""

import pandas as pd
import sure


class DataReader(object):
    """docstring for DataReader"""
    def __init__(self, file_name):
        super(DataReader, self).__init__()
        self.file_name = file_name

    def read_data(arg):
        """
        Reads raw tweezer according to the argument specified
        """


class TweezerCalibrationValues(object):
    """
    Stores tweezer calibration values and metadata about the experiments
    """

    def __init__(self):
        pass

    @property
    def units(self, quantity):
        try:
            if not isinstance(quantity, str):
                raise TypeError
        except TypeError, e:
            print('We need a string here to query the dictionary')

        reference_units = self._reference_units()
        units = dict()

        print('Units of {} : [{}]'.format(quantity, 'test'))

    def print_units(self):
        """
        Prints the units of the tweezer experiments in a formatted table.
        """
        
        units = self.units()

        for keys, values in units.items():
            print("{} : {}".format(keys, values))

    def _reference_units(self):
        """
        Contains a dictionary of all the units used in tweezer experiments.
        """
        reference_units = dict()
        reference_units = {   'date': ['day', 'month', 'year'],
                    'time_of_experiment': ['hour', 'minute', 'second'],
                    'laser_diode_temperature': 'C',
                    'laser_diode_operating_hours': 'h',
                    'laser_diode_current': 'A',
                    'aod_andor_center_x': 'px',
                    'aod_andor_center_y': 'px',
                    'aod_andor_range_x': 'px',
                    'aod_andor_range_y': 'px',
                    'aod_ccd_center_x': 'px',
                    'aod_ccd_center_y': 'px',
                    'aod_ccd_range_x': 'px',
                    'aod_ccd_range_y': 'px',
                    'pm_andor_center_x': 'px',
                    'pm_andor_center_y': 'px',
                    'pm_andor_range_x': 'px',
                    'pm_andor_range_y': 'px',
                    'pm_ccd_center_x': 'px',
                    'pm_ccd_center_y': 'px',
                    'pm_ccd_range_x': 'px',
                    'pm_ccd_range_y': 'px',
                    'andor_pixel_size_x': 'nm',
                    'andor_pixel_size_y': 'nm',
                    'ccd_pixel_size_x': 'nm',
                    'ccd_pixel_size_y': 'nm',
                    'aod_detector_x_offset': 'V',
                    'aod_detector_y_offset': 'V',
                    'aod_trap_stiffness_x': 'pN/nm',
                    'aod_trap_stiffness_y': 'pN/nm',
                    'aod_trap_distance_conversion_x': 'MHz/px',
                    'aod_trap_distance_conversion_y': 'MHz/px',
                    'pm_detector_x_offset': 'V',
                    'pm_detector_y_offset': 'V',
                    'pm_trap_stiffness_x': 'pN/nm',
                    'pm_trap_stiffness_y': 'pN/nm',
                    'pm_trap_distance_conversion_x': 'V/px',
                    'pm_trap_distance_conversion_y': 'V/px',
                    'aod_bead_radius': 'um',
                    'pm_bead_radius': 'um',
                    'sampling_rate': 'Hz',
                    'number_of_samples': 'unitless',
                    'time_step': 's'}

        return reference_units

    def _print_reference_units(self):
        """
        Prints the reference units of the tweezer experiments in a formatted table.
        """
        reference_units = self._reference_units()

        for keys, values in reference_units.items():
            print("{} : {}".format(keys, values))


def find_files(files, regex_pattern, verbose=False):
    """
    Finds all files in a list that matches a certain pattern.

    Parameters:
    """"""""""""

        files           : list of files
        regex_pattern   : regular expression pattern
        verbose         : whether or not to print extra information

    Returns:
    """"""""
    
        files_found     : list of files that matches the pattern

    """
    if files:
        if not all([isinstance(i, str) for i in files]):
            raise TypeError('Expects a list of strings representing file paths.')


    files_found = []
    
    for iFile in files:
        match = re.findall(regex_pattern, iFile)
        if match:
            files_found.append(iFile)
            if verbose:
                print("Found file: {}".format(iFile))

        else:
            if verbose:
                print("Pattern not found!")
        
    return files_found

