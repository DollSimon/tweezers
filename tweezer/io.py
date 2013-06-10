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
import envoy
from nptdms import TdmsFile


from tweezer.ixo import TweebotDictionary
from tweezer.core.parsers import parse_tweezer_file_name


def read_tweezer_txt(file_name):
    """
    Reads dual-trap data and metadata contained in text files
    """
    # check file sanity and correct it if necessary
    shell_call = envoy.run('tail -n 12 {}'.format(file_name), timeout=5)
    if shell_call.status_code is 0:
        tail = shell_call.std_out.split("\n")

    if any([l.strip().startswith("#") for l in tail]):
        is_file_sane = False 
    else:
        is_file_sane = True

    with open(file_name, 'r') as f:
        lines = f.readlines()

    return lines, is_file_sane


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


def read_thermal_calibration(file_name, frequency=80000):
    """
    Reads time series and calculated power spectra of a thermal calibration.

    :param file_name: (path) to the tweezer time series file containing the raw values of the PSD signals

    :param frequency: (int) sampling frequency of time series
    
    :return ts: (pandas.DataFrame) with the raw thermal calibration data. The index is time.
    
    """
    # get header information
    with open(file_name, 'r') as f:
        fl = f.readlines(1000)

    # finding the date; if any error occurs take the current date and time
    comments = [line for line in fl[0:15] if line.strip().startswith('#')] 

    try:
        date_string = [l.strip().replace("\t", " ").split(": ")[-1] for l in comments if 'Date' in l][0]
        date = datetime.datetime.strptime(date_string, '%m/%d/%Y %H:%M %p')
    except:
        date = datetime.datetime.now()

    try:
        nSamples = int(float([l.strip().split(": ")[-1] for l in comments if 'samples' in l][0]))
    except:
        nSamples = 2**20

    # time step in seconds
    dt = 1.0/frequency
    time = [dt*i for i in xrange(nSamples)]

    # read header information
    header_pos = [ind for ind, line in enumerate(fl[0:15]) if re.match('^[a-zA-Z]', line.strip())][-1]
    header = fl[header_pos]
    columns = [col.replace('.', '_').strip() for col in header.strip().split('\t')]

    data_pos = [ind for ind, line in enumerate(fl[0:45]) if re.match('^[-0-9]', line.strip())][0]
    # read file data
    ts = pd.read_table(file_name, sep='\t', skiprows=data_pos, 
        names=columns, header=None)

    # setting time as a data column and an index to be on the safe side
    ts['time'] = time
    ts.index = time

    # pass date as an attribute 
    ts.date = date
    ts.nSamples = nSamples

    return ts


def read_tweezer_power_spectrum(file_name):
    """
    Reads data from tweezer power spectrum file. These files are produced by LabView and contain the raw PSDs and the fits used to extract trap calibration results
    
    :param file_name: (path) file path to the tweezer power spectrum file

    :return psd: (pandas.DataFrame) with all the raw and fitted data as well as the fit results
    """
    # get header information
    with open(file_name, 'r') as f:
        fl = f.readlines(1000)

    # parsing header information
    comments = [line.strip().strip("# ") for line in fl[0:40] if line.strip().startswith('#')] 

    units = {}
    fit_results = {}

    for line in comments:
        if 'Date' in line:
            try:
                date_string = line.split(": ")[-1].replace("\t", " ")
                date = datetime.datetime.strptime(date_string, '%m/%d/%Y %H:%M %p') 
            except:
                date = datetime.datetime.now()
        elif 'nSamples' in line:
            try:
                nSamples = int(float(line.strip().split(": ")[-1]))
            except:
                nSamples = 2**20
        elif 'nBlocks' in line:
            try:
                nBlocks = int(float(line.strip().split(": ")[-1]))
            except:
                nBlocks = 128
        elif 'sampleRate' in line:
            try:
                sampleRate = int(float(line.strip().split(": ")[-1]))
            except:
                sampleRate = 80000
        else:
            if ":" in line:
                parts = line.split(": ")
            elif re.search('\w\s(\d|-\d)', line):
                parts = line.split(" ")

            if "." in parts[0]:
                var, unit, value = parts[0].split(".")[0], parts[0].split(".")[1], float(parts[1])
            else:
                var, unit, value = parts[0], None, float(parts[1])

            units[var] = unit
            fit_results[var] = value

    # getting header and data
    header_pos = [ind for ind, line in enumerate(fl[0:45]) if re.match('^[a-zA-Z]', line.strip())][-1]
    header = fl[header_pos]
    columns = [col.replace('.', '_').strip() for col in header.strip().split('\t')]

    data_pos = [ind for ind, line in enumerate(fl[0:45]) if re.match('^[-0-9]', line.strip())][0]

    # read file data
    psd = pd.read_table(file_name, sep='\t', skiprows=data_pos, 
        names=columns, header=None)

    psd.date = date
    psd.nSamples = nSamples
    psd.nBlocks = nBlocks
    psd.sampleRate = sampleRate

    for k, v in fit_results.iteritems():
        psd.__setattr__(k, v)

    psd.units = units

    return psd


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
    info = parse_tweezer_file_name(file_name, parser='bot_tdms')

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
        index = pd.date_range(start = info.date, periods = len(df), freq = '{}U'.format(int(1000000.0/frequency)))
        df.index = index
    else:
        index = pd.date_range(start = datetime.datetime.now(), periods = len(df), freq = '{}U'.format(int(1000000.0/frequency))  )
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


def gather_tweebot_data(trial=1, subtrial=None):
    pass

