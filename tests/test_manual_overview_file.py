#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os, shutil

import sure
import unittest
import nose

import pandas as pd

from collections import namedtuple

from clint.textui import colored, puts, indent

try:
    import simplejson as json
except:
    import json

try:
    from rpy2.robjects import r
    import pandas.rpy.common as com
except:
    raise ImportError('Probably the rpy2 library is not working...')

try:
    from tweezer import _DEFAULT_SETTINGS
    from tweezer import _TWEEBOT_CONFIG
    from tweezer import path_to_sample_data
    from tweezer import read
    from tweezer.cli.utils import list_tweezer_files, sort_files_by_trial
    from tweezer.cli.utils import collect_data_per_trial
except ImportError, err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')


class TestSimpleOverviewPage:

    @classmethod
    def setup_class(cls):
        print ("setup_class() before any methods in this class")
        cls.current_dir = os.getcwd()
        cls.data_path = os.path.expanduser('~/code/example_data/manual')
        os.chdir(cls.data_path)
        cls.files = list_tweezer_files(os.getcwd())

    @classmethod
    def teardown_class(cls):
        print ("teardown_class() after any methods in this class")
        os.chdir(cls.current_dir)

    def setUp(self):
        self.x = 4
        # read data
        # man_file = path_to_sample_data()

    def tearDown(self):
        pass

    def test_correct_location(self):
        os.getcwd().should.equal(self.__class__.data_path) 
        content = os.listdir(os.getcwd()) 
        ('data').should.be.within(content)
        ('thermal_calibration').should.be.within(content)
        ('distance_calibration').should.be.within(content)

    def test_get_list_of_available_files(self):
        files = self.__class__.files
        ('/Users/jahnel/code/example_data/manual/data/2.txt').shouldnot.be.within(files)
        ('/Users/jahnel/code/example_data/manual/thermal_calibration/PSD_4_e.txt').shouldnot.be.within(files)
        'man_data'.should.be.within(files)

    def test_files_per_trial(self):
        files = self.__class__.files
        tf = sort_files_by_trial(files=files)
        ('4_c').should.be.within(tf.keys())
        len(tf['4_c']).should.be(4)
        ('2').should.be.within(tf.keys())
        ('4_f').should.be.within(tf.keys())
        ('2_c').should.be.within(tf.keys())
        tf['4_c']['tc_psd'].shouldnot.equal([None]) 
        
    # def test_read_data_per_trial(self):
    #     files = self.__class__.files
    #     tf = sort_files_by_trial(files=files)
    #     TD = collect_data_per_trial(tf['4_c'])
    #     TD.man_data.should.be.a(namedtuple) 
        
