#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil

import unittest
import sure
import pytest
import nose
from nose.tools import *

from tweezer.cli.utils import collect_files_per_trial, list_tweezer_files
from tweezer.cli.utils import sort_files_by_trial
from tweezer.ixo.os_ import get_subdirs, get_new_subdirs
from tweezer.core.analysis import set_up_directories

# preparation
CURRENT = os.getcwd()
ROOT = '/Users/jahnel/code/example_data/tweebot'

def setUpModule():
    os.chdir(ROOT)


def tearDownModule():
    os.chdir(CURRENT)


class TestTweebotOverviewDirectoryStructure():

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

    def setUp(self):
        os.chdir(ROOT)

    def tearDown(self):
        pass

    def test_module_path(self):
        os.getcwd().should.equal(ROOT) 

    def test_establishment_of_correct_directory_structure(self):
        sorted_files = self.__class__.sorted_files
        set_up_directories(sorted_files, ROOT)
        current_dirs = get_subdirs(ROOT)

        analysis = os.path.join(ROOT, 'analysis')
        archive = os.path.join(ROOT, 'archive')
        overviews = os.path.join(ROOT, 'overviews')

        analysis.should.be.within(current_dirs)
        archive.should.be.within(current_dirs)
        overviews.should.be.within(current_dirs)

        os.chdir(overviews)
        o_dirs = get_subdirs(os.getcwd())

        trial_18 = os.path.join(ROOT, 'overviews', 'trial_18')
        trial_19 = os.path.join(ROOT, 'overviews', 'trial_19')
        trial_20 = os.path.join(ROOT, 'overviews', 'trial_20')
        trial_60 = os.path.join(ROOT, 'overviews', 'trial_60')
        trial_61 = os.path.join(ROOT, 'overviews', 'trial_61')

        trial_18.should.be.within(o_dirs)
        trial_19.shouldnot.be.within(o_dirs)
        trial_20.should.be.within(o_dirs)
        trial_60.should.be.within(o_dirs)
        trial_61.should.be.within(o_dirs)

        os.chdir(archive)
        a_dirs = get_subdirs(os.getcwd())

        trial_18 = os.path.join(ROOT, 'archive', 'trial_18')
        trial_19 = os.path.join(ROOT, 'archive', 'trial_19')
        trial_20 = os.path.join(ROOT, 'archive', 'trial_20')
        trial_60 = os.path.join(ROOT, 'archive', 'trial_60')
        trial_61 = os.path.join(ROOT, 'archive', 'trial_61')

        trial_18.should.be.within(a_dirs)
        trial_19.shouldnot.be.within(a_dirs)
        trial_20.should.be.within(a_dirs)
        trial_60.should.be.within(a_dirs)
        trial_61.should.be.within(a_dirs)
        

