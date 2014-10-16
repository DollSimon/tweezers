#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

from clint.textui import colored, puts, indent


try:
    from tweezer.legacy.cli.utils import collect_files_per_trial
    from tweezer.legacy.cli.utils import list_tweezer_files
    from tweezer.legacy.cli.utils import sort_files_by_trial
    from tweezer.legacy.cli.utils import collect_data_per_trial
except ImportError as err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')


# preparation
CURRENT = os.getcwd()
ROOT = '/Users/jahnel/code/example_data/tweebot'

def setUpModule():
    os.chdir(ROOT)


def tearDownModule():
    os.chdir(CURRENT)


class TestCollectFilesPerTrial:
    """
    TestCollectFilesPerTrial covers:
    ================================

    Given a list of files in a directory, this function sorts it into files belonging to a certain trial
    """

    def __init__(self):
        self.files = list_tweezer_files(ROOT, cache_results=False)

    def test_module_path(self):
        os.getcwd().should.equal(ROOT) 

    def test_files_list_is_generated(self):
        files = self.files 
        files.shouldnot.be.empty
        
    def test_collection_gets_correct_files(self):
        files = self.files 
        collected_files = collect_files_per_trial(files, trial=18)

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

    def test_collect_files_with_several_logs(self):
        trial_files = collect_files_per_trial(trial=61, files=self.files)
        trial_files['bot_log'].should.equal(['/Users/jahnel/code/example_data/tweebot/logs/61.TweeBotLog.2013.02.20.10.04.32.txt', '/Users/jahnel/code/example_data/tweebot/logs/61.TweeBotLog.2013.02.20.10.05.23.txt'])

    def test_sorting_of_files(self):
        files = self.files 
        sorted_files = sort_files_by_trial(files, sort_by='bot_data')

        ('18').should.be.within(sorted_files)
        ('20').should.be.within(sorted_files)
        ('60').should.be.within(sorted_files)
        ('61').should.be.within(sorted_files)

        'man_data'.shouldnot.be.within(sorted_files['18'])

        # test that there is no manual file types
        keys = [key for key in sorted_files['18']]
        'man'.shouldnot.be.within(keys)
        
    def test_reading_data(self):
        files = self.files 
        sorted_files = sort_files_by_trial(files, sort_by='bot_data')
        TrialData = collect_data_per_trial(sorted_files['18'])
    
        TrialData.shouldnot.be.empty
        
    
     
    



