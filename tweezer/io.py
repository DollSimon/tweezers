"""
Input/Output routines for the tweezer package.

Performs file reads and data conversion.
"""

import pandas as pd
import numpy as np

def read_tweezer_txt(file_name):
    """
    Reads dual-trap data and metadata contained in text files
    """
    with open(file_name, 'r') as f:
        lines = f.readlines()

    return lines


def read_tweebot_txt(file_name):
    """
    Reads dual-trap data and metadata from TweeBot datalog files.

    Parameters:
    """"""""""""

      file_name: Path to the TweeBot datalog file.


    Returns:
    """""" 

        df: Pandas DataFrame containing the recorded data

        calibration: Dictionary containing the metadata of the experiment


    Usage
    """"""
    >>> df, cal = read_tweebot_txt('27.Datalog.2013.02.17.19.42.09.datalog.txt')
    """
    column_names, calibration, header_line = read_tweebot_header(file_name)

    df = pd.read_table(file_name, header = header_line)

    # get rid of unnamed and empty colums
    df = df.dropna(axis = 1)

    # set index as time and column names
    print(calib['Delta time (s)'])
    
    df.columns = column_names

    return df, calibration 


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


def read_tweebot_header(datalog_file, calibration_as_dict = True):
    """
    Extracts the header of a Tweebot data log file as a list

    Parameters:
    """"""""""""
        datalog_file :          Tweebot datalog file from which the header is extracted

        calibration_as_dict :   Boolean, whether to return calibration data as list or dictionary [True]


    Returns:
    """"""

        column_names :  Column names corresponding to the recorded variables

        calib_data :    Calibration data - dictionary [default] or list

        header_line :   Line of the header line with column names

    Usage:
    """"""
    >>> col, cal, header_line = read_tweebot_header('27.Datalog.2013.02.17.19.42.09.datalog.txt')
    >>> col, cal, header_line = read_tweebot_header('27.Datalog.2013.02.17.19.42.09.datalog.txt', calibration_as_dict = False)
    """
    column_names = []
    calibration_list = []
    line_count = 0

    with open(datalog_file, 'r') as f:

        first_lines = f.readlines(6000)

        for line in first_lines:

            line_count += 1

            if 'Message' in line or 'Force' in line:
                column_names = line.strip('\t\n\r').split('\t')
                header_line = line_count

            elif '#' in line[0:2] and ":" in line:
                calibration_list.append(line.strip().strip('\t\n\r').strip('#').strip())

    if calibration_as_dict:

        calib_data = {}

        for line in calibration_list:
            try: 
                calib_data[line.split(': ')[0]] = np.float32(line.split(': ')[1])
            except ValueError:
                calib_data[line.split(': ')[0]] = line.split(': ')[1]

    else:
        calib_data = calibration_list

    return column_names, calib_data, header_line

