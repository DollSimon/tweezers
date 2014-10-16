#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

import envoy
from colorama import init
from clint.textui import puts, indent, colored


try:
    from tweezer.legacy.cli.utils import list_tweezer_files
    from tweezer.legacy.cli.utils import CACHING_FILE
except ImportError as err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.'))
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err)))
        puts('')

init()

class TestTweezerListFiles:
    """
    TestTweezerListFiles covers:
    ============================

    * finding and listing of tweezer data files in a directory (recursive)
    """
    @classmethod
    def setup_class(cls):
        """
        Runs before any method in this test class
        """
        cls.current_dir = os.getcwd()
        cls.data_path = os.path.expanduser('~/code/example_data/manual')
        os.chdir(cls.data_path)

        cls.content = os.listdir(os.getcwd())

        # test for file list cache
        if CACHING_FILE in cls.content:
            cls.hasCacheBefore = True
        else:
            cls.hasCacheBefore = False

        cls.nFilesBefore = int(envoy.run('find . -type f | wc -l').std_out.strip())

        cls.files = list_tweezer_files(cls.data_path)

        cls.content = os.listdir(os.getcwd())

        if CACHING_FILE in cls.content:
            cls.hasCacheAfter = True
        else:
            cls.hasCacheAfter = False

        cls.nFilesAfter = int(envoy.run('find . -type f | wc -l').std_out.strip())

    @classmethod
    def teardown_class(cls):
        """
        Runs after all methods in this test class
        """
        os.chdir(cls.data_path)

        cached_file = os.path.join(os.getcwd(), CACHING_FILE)
        if os.path.exists(cached_file) and not cls.hasCacheBefore:
            os.remove(cached_file)

        os.chdir(cls.current_dir)

    def test_correct_location(self):
        os.getcwd().should.be(os.path.expanduser('~/code/example_data/manual'))

        if not self.__class__.hasCacheBefore:
            (self.__class__.hasCacheAfter).should.be.true

    def test_file_listing_exists(self):
        files = self.__class__.files

        files.should.be.a('collections.defaultdict')
        ('man_data').should.be.within(files)
        ('directory_state').should.be.within(files)
        ('man_aod_dist_cal_mat').should.be.within(files)
        ('man_pm_dist_cal_mat').should.be.within(files)
