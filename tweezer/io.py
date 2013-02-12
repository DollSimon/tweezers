"""
Input/Output routines for the tweezer package.

Performs file reads and data conversion.
"""

import pandas as pd


def read_tweezer_txt(file_name):
    """
    Reads dual-trap data and metadata contained in text files
    """
    with open(file_name, 'r') as f:
        lines = f.readlines()

    return lines


def read_tweebot_txt(file_name):
    """
    Reads dual-trap data and metadata from TweeBot text files
    """
    with open(file_name, 'r') as f:
        lines = f.readlines()

    return lines


def read_tweezer_mat(file_name):
    """
    Reads data from Matlab file
    """
    pass


def read_tweezer_r(file_name):
    """
    Reads data from R file.
    """
    pass


def read_tdms(file_name):
    """
    Reads data from Labview TDMS file.
    """
    pass


def read_tweebot_stats(file_name):
    """
    Reads data from TweeBot statistic files.
    """
    pass


def read_tweebot_logs(file_name):
    """
    Reads data from TweeBot log files.
    """
    pass


def read_tracking_data(file_name):
    """
    Reads data from Tweezer Tracking files.
    """
    df = pd.read_csv(file_name, sep = '\t')
    return df
