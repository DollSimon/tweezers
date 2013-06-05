"""
Input/Output routines for the tweezer package.

Performs file reads and data conversion.
"""
import re
from collections import namedtuple, OrderedDict
import datetime

import pandas as pd
import numpy as np
import datetime as dt
import pytz
from nptdms import TdmsFile

from tweezer.ixo import TweebotDictionary, TweezerUnits
from tweezer.core.parsers import parse_tweebot_tdms_file_name


def read_tweezer_txt(file_name):
    """
    Reads dual-trap data and metadata contained in text files
    """
    with open(file_name, 'r') as f:
        lines = f.readlines()

    return lines


def read_tweebot_data(file_name, simplify_names=True):
    """
    Reads dual-trap data and metadata from TweeBot datalog files.

    :param file_name: Path to the TweeBot datalog file.
    :param simplify_names: (Bool) greatly simplifies the string representations of the varibles

    :return df: Pandas DataFrame containing the recorded data

    :return calibration: Dictionary containing the metadata of the experiment

    :return cal_units: Lookup Table for units of the calibration data

    Usage
    """"""
    >>> df, cal = read_tweebot_txt('27.Datalog.2013.02.17.19.42.09.datalog.txt')

    .. note::

        This function only works for TweeBot data files in the form of 2013

    """
    column_names, calibration, header_line = read_tweebot_data_header(file_name)

    df = pd.read_table(file_name, header = header_line)

    # get rid of unnamed and empty colums
    df = df.dropna(axis = 1)

    # set column names and index as time 
    if simplify_names:
        df.columns = simplify_tweebot_data_names(column_names)

    if 'Time sent (s)' in column_names:
        dates = pd.DatetimeIndex([dt.datetime.fromtimestamp(time) for time in df['Time sent (s)']])
        df.index = dates
    elif 'timeSent' in column_names:
        dates = pd.DatetimeIndex([dt.datetime.fromtimestamp(time) for time in df['timeSent']])
        df.index = dates
    else:
        print("No time index set: Could not find column 'Time sent (s)' in data")

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


def simplify_tweebot_data_names(variable_names):
    v = variable_names
    if 'Time sent (s)' in v:
        v[v.index('Time sent (s)')] = 'timeSent'

    if 'Time received (s)' in v:
        v[v.index('Time received (s)')] = 'timeReceived'

    if 'Experiment Phase (int)' in v:
        v[v.index('Experiment Phase (int)')] = 'experimentPhase'

    if 'Message index (int)' in v:
        v[v.index('Message index (int)')] = 'mIndex'

    if 'Extension from Trap and PSD positions (nm)' in v:
        v[v.index('Extension from Trap and PSD positions (nm)')] = 'extensionTrap'

    if 'Extension from image measurements (nm)' in v:
        v[v.index('Extension from image measurements (nm)')] = 'extenstionImage'

    if 'Force felt by AOD (pN)' in v:
        v[v.index('Force felt by AOD (pN)')] = 'forceAod'

    if 'Force felt by PM  (pN)' in v:
        v[v.index('Force felt by PM  (pN)')] = 'forcePm'

    if 'AOD to PM vector x (nm)' in v:
        v[v.index('AOD to PM vector x (nm)')] = 'trapDistX'

    if 'AOD to PM vector y (nm)' in v:
        v[v.index('AOD to PM vector y (nm)')] = 'trapDistY'

    if 'AODx (V)' in v:
        v[v.index('AODx (V)')] = 'dispAodX'

    if 'AODy (V)' in v:
        v[v.index('AODy (V)')] = 'dispAodY'

    if 'PMx (V)' in v:
        v[v.index('PMx (V)')] = 'dispPmX'

    if 'PMy (V)' in v:
        v[v.index('PMy (V)')] = 'dispPmY'

    if 'PMsensorx (V)' in v:
        v[v.index('PMsensorx (V)')] = 'mirrorX'

    if 'PMsensory (V)' in v:
        v[v.index('PMsensory (V)')] = 'mirrorY'

    if 'PMxdiff (V)' in v:
        v[v.index('PMxdiff (V)')] = 'pmX'

    if 'PMydiff (V)' in v:
        v[v.index('PMydiff (V)')] = 'pmY'

    if 'PMxsum (V)' in v:
        v[v.index('PMxsum (V)')] = 'pmS'

    if 'AODxdiff (V)' in v:
        v[v.index('AODxdiff (V)')] = 'aodX'

    if 'AODydiff (V)' in v:
        v[v.index('AODydiff (V)')] = 'aodY'

    if 'AODxsum (V)' in v:
        v[v.index('AODxsum (V)')] = 'aodS'

    if 'StageX (mm)' in v:
        v[v.index('StageX (mm)')] = 'stageX'

    if 'StageY (mm)' in v:
        v[v.index('StageY (mm)')] = 'stageY'

    if 'StageZ (mm)' in v:
        v[v.index('StageZ (mm)')] = 'stageZ'

    if 'Pressure (a.u.)' in v:
        v[v.index('Pressure (a.u.)')] = 'pressure'

    if 'FBx (V)' in v:
        v[v.index('FBx (V)')] = 'fbX'

    if 'FBy (V)' in v:
        v[v.index('FBy (V)')] = 'fbY'

    if 'FBsum(V)' in v:
        v[v.index('FBsum (V)')] = 'fbZ'

    return v


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


def read_tdms(file_name, frequency=1000):
    """
    Reads data from Labview TDMS file.

    :param file_name: (path) to tdms file

    :param frequency: (int) sampling frequency in Hz (default is 1000 Hz, i.e. data taken at 1 ms time resolution)

    :return df: (pd.DataFrame) with the channels as columns
    
    """
    info = parse_tweebot_tdms_file_name(file_name)

    # open tdms connection
    tf = TdmsFile(file_name)

    # read data
    if 'Untitled' in tf.groups():
        g = 'Untitled'
        df = pd.DataFrame(tf.channel_data(g, 'Untitled'), columns=['pmX'])
        df['pmY'] = tf.channel_data(g, 'Untitled 1')
        df['aodX'] = tf.channel_data(g, 'Untitled 2')
        df['aodY'] = tf.channel_data(g, 'Untitled 3')
        df['pmS'] = tf.channel_data(g, 'Untitled 4')
        df['aodS'] = tf.channel_data(g, 'Untitled 5')
        df['fbS'] = tf.channel_data(g, 'Untitled 6')
        df['mirrorX'] = tf.channel_data(g, 'Untitled 7')
        df['mirrorY'] = tf.channel_data(g, 'Untitled 8')
        df['fbX'] = tf.channel_data(g, 'Untitled 9')
        df['fbY'] = tf.channel_data(g, 'Untitled 10')
        df['pressure'] = tf.channel_data(g, 'Untitled 11')
        
    # set index; in pandas the alias for microsecond offset is 'U'
    if info.date:
        index = pd.date_range(start = info.date, period = len(df), freq = '{}U'.format(int(1000000.0/frequency)))
        df.index = index
    else:
        index = pd.date_range(start = datetime.datetime.now(), period = len(df), freq = '{}U'.format(int(1000000.0/frequency))  )
        df.index = index

    return df 


def read_tweebot_stats(file_name):
    """
    Reads data from TweeBot statistic files.
    """
    pass


def read_tweebot_logs(file_name):
    """
    Reads data from TweeBot log files.

    :param file_name: (path) Tweebot log file to be parsed
    
    :return log: (pd.DataFrame) with the logging data
    """
    log = pd.read_table(file_name)
    log.columns = ['time', 'kind', 'routine', 'message']
    log.index = pd.to_datetime(log.time)
    log.tz_localize('Europe/Berlin')
    log.drop('time', axis=1)

    return log


def read_tracking_data(file_name):
    """
    Reads data from Tweezer Tracking files.
    """
    df = pd.read_csv(file_name, sep = '\t')
    return df


def read_tweebot_data_header(datalog_file, dtype='DataFrame'):
    """
    Extracts the header of a Tweebot data log file as a list

    :param datalog_file : (path) Tweebot datalog file from which the header is extracted

    :param dtype: (Str) specifies the return type of the calibration data, either 'DataFrame' (default) or 'Dict' or 'List'
        

    :return calib_data :    Calibration data - pandas DataFrame (default), dictionary or list

    :return header_line :   Line of the header line with column names

    Usage:
    """"""
    >>> col, cal, header_line = read_tweebot_data_header('27.Datalog.2013.02.17.19.42.09.datalog.txt')
    >>> col, cal, header_line = read_tweebot_data_header('27.Datalog.2013.02.17.19.42.09.datalog.txt', calibration_as_dict = False)
    """
    column_names = []
    calibration_list = []
    line_count = 0

    dtype = dtype.upper()

    with open(datalog_file, 'r') as f:

        first_lines = f.readlines(6000)

        for line in first_lines:

            line_count += 1

            if 'Message' in line or 'Force' in line:
                column_names = line.strip('\t\n\r').split('\t')
                header_line = line_count

            elif '#' in line[0:2] and ":" in line:
                calibration_list.append(line.strip().strip('\t\n\r').strip('#').strip())

    calib_data = OrderedDict()

    for line in calibration_list:
        try: 
            calib_data[line.split(': ')[0]] = np.float32(line.split(': ')[1])
        except ValueError:
            calib_data[line.split(': ')[0]] = line.split(': ')[1]

    if dtype == 'DICT':
        calib_data = TweebotDictionary(*calib_data.values())
    elif dtype == 'DATAFRAME':
        calib_data = TweebotDictionary(*calib_data.values())._asdict()
        df = pd.DataFrame(dict(calib_data), columns=dict(calib_data).keys(), index=[1])
        df['timeStep'] = df['deltaTime']
        calib_data = df
    else:
        calib_data = calibration_list

    return column_names, calib_data, header_line


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
