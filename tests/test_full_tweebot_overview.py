#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import unittest
import sure
import pytest
import nose
from nose.tools import *

from tweezer.cli.utils import collect_files_per_trial, list_tweezer_files
from tweezer.cli.utils import sort_files_by_trial

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
        self.sorted_files = sort_files_by_trial(files, sort_by='bot_data')

    def test_module_path(self):
        os.getcwd().should.equal(ROOT) 

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
        trial_files['bot_log'].should.equal('/Users/jahnel/code/example_data/tweebot/logs/18.TweeBotLog.2013.02.19.22.43.07.txt')
        trial_files['bot_stats'].should.equal('/Users/jahnel/code/example_data/tweebot/stats/18.TweeBotStats.txt') 
        trial_files['bot_tdms'].should.equal('/Users/jahnel/code/example_data/tweebot/data/18_2013_05_19_17_18_07.tdms') 
        trial_files['bot_focus'].should.equal(None) 
        trial_files['bot_andor'].shouldnot.be.empty 
        trial_files['bot_ccd'].shouldnot.be.empty
    
    def test_read_data(self):
        trial_files = collect_files_per_trial(trial=18, files=self.files)

