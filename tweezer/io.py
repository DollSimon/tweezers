"""
Input/Output routines for the tweezer package.

Performs file reads and data conversion.
"""

import pandas as pd
import numpy as np
import re

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
    print(calibration['Delta time (s)'])
    if 'Delta time (s)' in calibration:
        df.index = calibration['Delta time (s)']
    df.columns = column_names


    return df, calibration 


def read_thermal_calibration(file_name):
    """
    Reads time series and calculated power spectra of a thermal calibration.
    """
    if is_calibration_time_series(file_name):

        print('Rocket!')
    elif is_calibration_spectrum(file_name):
        print('Rackoon!')
    else:
        print('Wrong file format or file type!')





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


def read_calibration_header(file_name):
    """
    Extracts the header information in tweezer thermal calibration files.

    Parameter:
    """"""""""""
      file_name: File under scrutiny, either the original time series or the spectra.
      type:        
    """



def is_calibration_time_series(file_name):
    """
    Checks whether file is a tweezer thermal calibration time series.

    Parameter:
    """"""""""""
      file_name:    File to check identity for.

    Return:
    """"""
      result:   Boolean, True for tweezer time series of the form 'TS_1_a.txt' 
    """
    TIME_SERIES_PATTERN = re.compile(r'(TS)_(\w)*_*(\d)+_*(\w)*(.txt)', re.IGNORECASE)

    if re.search(TIME_SERIES_PATTERN, file_name):
        result = True
    else:
        result = False

    return result 


def is_calibration_spectrum(file_name):
    """
    Checks whether file is a tweezer thermal calibration power spectrum.

    Parameter:
    """"""""""""
      file_name:    File to check identity for.

    Return:
    """"""
      result:   Boolean, True for tweezer thermal calibration spectrum of the form 'PSD_1_a.txt'
    """
    SPECTRUM_PATTERN = re.compile(r'(PSD)_(\w)*_*(\d)+_*(\w)*(.txt)', re.IGNORECASE)

    if re.search(SPECTRUM_PATTERN, file_name):
        result = True
    else:
        result = False

    return result 


def is_tweebot_datalog(file_name):
    """
    Checks whether file is a tweebot datalog file.

    Parameter:
    """"""""""""
      file_name:    File to check identity for.

    Return:
    """"""
      result:   Boolean, True for TweeBot datalog files of the form '27.Datalog.2012.11.27.05.34.16.datalog.txt'
    """
    DATALOG_PATTERN = re.compile(r'(\d)+.(Datalog)(.\d+)+.(datalog)(.txt)', re.IGNORECASE)

    if re.search(DATALOG_PATTERN, file_name):
        result = True
    else:
        result = False

    return result 


def is_tweebot_stats(file_name):
    """
    Checks whether file is a tweebot statistics file.

    Parameter:
    """"""""""""
      file_name:    File to check identity for.

    Return:
    """"""
      result:   Boolean, True for TweeBot statistics files of the form '27.TweeBotStatss.txt'
    """
    STATS_PATTERN = re.compile(r'(\d)+.(TweeBotStats)(\w)*(.txt)', re.IGNORECASE)

    if re.search(STATS_PATTERN, file_name):
        result = True
    else:
        result = False

    return result 


def is_tweebot_log(file_name):
    """
    Checks whether file is a tweebot log file.

    Parameter:
    """"""""""""
      file_name:    File to check identity for.

    Return:
    """"""
      result:   Boolean, True for TweeBot log files of the form '27.TweeBotLog.2013.02.20.01.16.33.txt'
    """
    LOG_PATTERN = re.compile(r'(\d)+.(TweeBotLog)(.\d+)+(.txt)', re.IGNORECASE)

    if re.search(LOG_PATTERN, file_name):
        result = True
    else:
        result = False

    return result 

def is_tweezer_data(file_name):
    """
    Checks whether file is a tweezer data file (manually recorded).

    Parameter:
    """"""""""""
      file_name:    File to check identity for.

    Return:
    """"""
      result:   Boolean, True for Tweezer data files of the form 'pre_27_a.txt' in the 'data' directory.
    """
    DATA_PATTERN = re.compile(r'(\w*)_*(\d+)?_*(\w*)(.txt)', re.IGNORECASE)

    if re.search(DATA_PATTERN, file_name):
        result = True
    else:
        result = False

    if 'PSD' in file_name:
        result = False
    elif 'TS' in file_name:
        result = False
    elif len(file_name.split('.')) > 2:
        result = False

    return result 
