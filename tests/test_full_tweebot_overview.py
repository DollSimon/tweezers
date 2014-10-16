#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

from tweezer.legacy.cli.utils import list_tweezer_files
from tweezer.legacy.cli.utils import sort_files_by_trial

# preparation
ORIGINAL = os.getcwd()
ROOT = '/Users/jahnel/code/example_data/tweebot'

def setUpModule():
    os.chdir(ROOT)

def tearDownModule():
    os.chdir(ORIGINAL)


class TestTweebotOverview():

    @classmethod
    def setup_class(cls):
        """
        Runs before any method in this test class
        """
        os.chdir(ROOT)
        cls.pre_subdirs = get_subdirs(ROOT)
        cls.files = list_tweezer_files(ROOT)
        cls.sorted_files = sort_files_by_trial(cls.files, sort_by='bot_data')

    
    @classmethod
    def teardown_class(cls):
        """
        Runs after all methods in this test class
        """
        os.chdir(ROOT)
        post_subdirs = get_subdirs(ROOT)
        pre_subdirs = cls.pre_subdirs

        new_dirs = get_new_subdirs(pre_subdirs, post_subdirs)

        for d in new_dirs:
            shutil.rmtree(d)



