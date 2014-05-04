#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pytest

import os

from clint.textui import colored, puts, indent

try:
    from tweezer.cli.utils import list_tweezer_files
except ImportError as err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')


@pytest.fixture
def files():
    dataPath = os.path.expanduser('~/code/example_data/manual/distance_calibration')    
    dataFiles = list_tweezer_files(dataPath, cache_results=False)
    return dataFiles


def test_files_are_found_at_location(files):
    assert files is not None


def test_content_of_file_list(files):
    assert 'man_pm_dist_cal_res' in files
    assert 'man_aod_dist_cal_res' in files
    assert 'man_dist_cal_tmp' in files


def test_values_of_calibration_files_can_be_read(files):
    assert False
