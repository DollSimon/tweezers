#!/usr/bin/env python
# coding=utf-8
"""
Analysis of Tweezer Experiments
"""
import os


def set_up_directories(filesByTrial: list, root: str):
    """
    Creates directories for the analysis

    :param list filesByTrial: nested dictionary of trials and their related files
    :param str root: root directory of a tweezer experiment
    """
    # avoid side effects for upstream functions
    DIR_ORIGINAL = os.getcwd()

    os.chdir(root)

    # creating main directories
    try:
        os.makedirs('overviews')
        os.makedirs('analysis')
        os.makedirs('archive')
    except OSError as err:
        if not os.path.isdir(err.filename):
            raise

    # creating directories for individual trials
    for file in filesByTrial:
        label = "trial_{}".format(file)
        try:
            os.makedirs(os.path.join('overviews', label))
            os.makedirs(os.path.join('archive', label))
            os.makedirs(os.path.join('analysis', label))
        except OSError as err:
            # be happy if someone already created
            if not os.path.isdir(err.filename):
                raise

    # get back to where you have been
    os.chdir(DIR_ORIGINAL)


def read_data_and_save(filesByTrial, root):
    """
    :param str root: Rocket
    """
    pass


def is_trial_complete(trial: str, root: str):
    """
    Checks whether for a given manual trial all raw data can be found in the
    *root* directory.

    This function looks for the data file, the thermal calibration files and
    more associated with the given trial.

    :param str trial: Trial name, e.g. '1', '2_b', 'new_4_c', etc.
    :param str root: Path of the main directory in which to search for all the associated files.

    :return bool isTrialComplete:
    """
    pass
