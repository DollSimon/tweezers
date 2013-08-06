#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import unittest
import sure
import pytest
import nose
from nose.tools import *

from tweezer.cli.utils import collect_files_per_trial, list_tweezer_files

# preparation
CURRENT = os.getcwd()
ROOT = '/Users/jahnel/code/example_data/tweebot'

def setUpModule():
    os.chdir(ROOT)


def tearDownModule():
    os.chdir(CURRENT)


class TestTweebotOverview():

    def __init__(self):
        self.files = list_tweezer_files(ROOT)

    def test_module_path(self):
        os.getcwd().should.equal(ROOT) 

    def test_assert(self):
        (4).shouldnot.equal(5) 

    def test_collect_files_of_nonexistent_trial(self):
        trial_files = collect_files_per_trial(trial=4, files=self.files)
        trial_files['bot_data'].should.be.none 
        trial_files['bot_log'].should.be.none 
        trial_files['bot_stats'].should.be.none 
        trial_files['bot_tdms'].should.be.none 
        trial_files['bot_focus'].should.be.none 
        trial_files['bot_andor'].should.be.none 
        trial_files['bot_ccd'].should.be.none 
        
    def test_collect_files_of_existent_trial(self):
        trial_files = collect_files_per_trial(trial=18, files=self.files)
        trial_files['bot_data'].should.equal('/Users/jahnel/code/example_data/tweebot/datalog/18.Datalog.2013.02.19.23.09.24.datalog.txt') 
        trial_files['bot_log'].shouldnot.be.empty 
        trial_files['bot_stats'].should.equal('/Users/jahnel/code/example_data/tweebot/stats/18.TweeBotStats.txt') 
        trial_files['bot_tdms'].should.equal(None) 
        trial_files['bot_focus'].should.equal(None) 
        trial_files['bot_andor'].shouldnot.be.empty 
        trial_files['bot_ccd'].shouldnot.be.empty
    
