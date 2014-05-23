#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import shutil

import pytest
from pathlib import Path

from tweezer.cli.utils import collect_files_per_trial, list_tweezer_files
from tweezer.cli.utils import sort_files_by_trial
from tweezer.ixo.os_ import get_subdirs, get_new_subdirs
from tweezer.core.analysis import set_up_directories

# preparation
CURRENT = os.getcwd()
ROOT = os.path.expanduser('~/code/example_data/tweebot')


@pytest.fixture
def sortedFilesList(request):

    os.chdir(ROOT)
    oldSubDirs = get_subdirs(ROOT)
    files = list_tweezer_files(ROOT)
    sortedFiles = sort_files_by_trial(files, sort_by='bot_data')

    def finalizer():
        print("Removing temporary test directories...")
        newSubDirs = get_subdirs(ROOT)
        newDirs = get_new_subdirs(oldSubDirs, newSubDirs)
        for d in newDirs:
            shutil.rmtree(d)

    request.addfinalizer(finalizer)
    return sortedFiles


def setup_module(module):
    """
    Runs before the module
    """
    os.chdir(ROOT)


def teardown_module(module):
    """
    Runs after the tests in this module
    """
    os.chdir(CURRENT)


def test_correct_directory_position():
    assert os.getcwd() == ROOT


def test_establishment_of_correct_directory_structure(sortedFilesList):
    set_up_directories(sortedFilesList, ROOT)
    currentDirs = get_subdirs(ROOT)

    analysis = os.path.join(ROOT, 'analysis')
    archive = os.path.join(ROOT, 'archive')
    overviews = os.path.join(ROOT, 'overviews')

    assert analysis in currentDirs
    assert archive in currentDirs
    assert overviews in currentDirs

    dirsInOverviews = get_subdirs(os.path.join(ROOT, 'overviews'))

    trial_18 = os.path.join(ROOT, 'overviews', 'trial_18')
    trial_19 = os.path.join(ROOT, 'overviews', 'trial_19')
    trial_20 = os.path.join(ROOT, 'overviews', 'trial_20')
    trial_60 = os.path.join(ROOT, 'overviews', 'trial_60')
    trial_61 = os.path.join(ROOT, 'overviews', 'trial_61')

    assert trial_18 in dirsInOverviews
    assert trial_19 not in dirsInOverviews
    assert trial_20 in dirsInOverviews
    assert trial_60 in dirsInOverviews
    assert trial_61 in dirsInOverviews

    dirsInArchive = get_subdirs(os.path.join(ROOT, 'archive'))
    trial_18 = os.path.join(ROOT, 'archive', 'trial_18')
    trial_19 = os.path.join(ROOT, 'archive', 'trial_19')
    trial_20 = os.path.join(ROOT, 'archive', 'trial_20')
    trial_60 = os.path.join(ROOT, 'archive', 'trial_60')
    trial_61 = os.path.join(ROOT, 'archive', 'trial_61')

    assert trial_18 in dirsInArchive
    assert trial_19 not in dirsInArchive
    assert trial_20 in dirsInArchive
    assert trial_60 in dirsInArchive
    assert trial_61 in dirsInArchive
