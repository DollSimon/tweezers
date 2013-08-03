#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest
import sure

import os

from clint.textui import colored, puts, indent

try:
    from tweezer.cli.utils import list_tweezer_files
except ImportError, err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')


class TestDistanceCalibrationIO:
    """
    TestDistanceCalibrationIO covers:
    =================================

    * finding tweezer distance calibration files for both traps
    * reading data into common data structure 
    """

    @classmethod
    def setup_class(cls):
        """
        Runs before any method in this test class
        """
        cls.current_dir = os.getcwd()
        cls.data_path = os.path.expanduser('~/code/example_data/manual/distance_calibration')
        os.chdir(cls.data_path)

        cls.files = list_tweezer_files(cls.data_path, cache_results=False)
    
    @classmethod
    def teardown_class(cls):
        """
        Runs after all methods in this test class
        """
        os.chdir(cls.current_dir)

    def test_location(self):
        files = self.__class__.files
        files.shouldnot.be.empty

        ('man_pm_dist_cal_res').should.be.within(files)
        ('man_aod_dist_cal_res').should.be.within(files)
        ('man_dist_cal_tmp').should.be.within(files)
        
    def test_read_distance_calibration_results_for_pm(self):
        files = self.__class__.files
        files.shouldnot.be.empty
        
        


