#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os, shutil

import sure
import unittest
import nose

import pandas as pd

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
    from tweezer.cli.utils import list_tweezer_files
except ImportError, err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')


class TestTweebotOverviewPage:

    @classmethod
    def setup_class(cls):
        print ("setup_class() before any methods in this class")
        cls.current_dir = os.getcwd()
        cls.data_path = os.path.expanduser('~/code/example_data/tweebot')
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
        ('datalog').should.be.within(content)
        ('logs').should.be.within(content)
        ('stats').should.be.within(content)

    def test_get_list_of_available_files(self):
        files = self.__class__.files
        ('/Users/jahnel/code/example_data/tweebot/datalog/20.Datalog.2013.02.19.23.32.22.datalog.txt').shouldnot.be.within(files)
        ('/Users/jahnel/code/example_data/tweebot/logs/20.TweeBotLog.2013.02.19.23.26.55.txt').shouldnot.be.within(files)
        'bot_data'.should.be.within(files)
        
