"""
Input/Output routines for the tweezer package.

Performs file reads and data conversion.
"""
import re
from collections import namedtuple, OrderedDict
import datetime

import pandas as pd
import numpy as np
import envoy
from nptdms import TdmsFile


from tweezer.ixo import TweebotDictionary, extract_meta_and_units, simplify_tweebot_data_names
from tweezer.core.parsers import parse_tweezer_file_name


def read_tweezer_txt(file_name):
    """
    Reads dual-trap data and metadata contained in text files
    """
    # check file sanity and correct it if necessary
    shell_call = envoy.run('tail -n 12 {}'.format(file_name), timeout=5)
    if shell_call.status_code is 0:
        tail = shell_call.std_out.split("\n")
    else:
        raise IOError("The file {} does not exist".format(file_name))

    if any([l.strip().startswith("#") for l in tail]):
        isFileSane = False 
    else:
        isFileSane = True

    with open(file_name, 'r') as f:
        fl = f.readlines(1000)

    # parsing header information
    header_comments = [line.strip().strip("# ") for line in fl[0:40] if line.strip().startswith('#')] 
    tail_comments = [line.strip().strip("# ") for line in tail[-10:] if line.strip().startswith('#')] 
    comments = header_comments + tail_comments

    CommentInfo = extract_meta_and_units(comments)

    units = CommentInfo.units
    meta = CommentInfo.metadata

    meta['originalFile'] = file_name
    meta['isFileSane'] = isFileSane

    # getting header and data
    header_pos = [ind for ind, line in enumerate(fl[0:45]) if re.match('^[a-zA-Z]', line.strip())][-1]
    header = fl[header_pos]
    column_precursor = [col.strip() for col in header.strip().split('\t')]

    columns = []
    for c in column_precursor:
        if re.search('\(([a-zA-Z]+)\)', c):
            name, unit = re.search('^(\w+)\s+\(([a-zA-Z]+)\)', c).groups()
            columns.append(name)
            units[name] = unit
        else:
            columns.append(c)

    data_pos = [ind for ind, line in enumerate(fl[0:45]) if re.match('^[-0-9]', line.strip())][0]

    data = pd.read_table(file_name, sep='\t', header=None, skiprows=data_pos,
        names=columns)

    # drop rows with "NaN" values
    data = data.dropna()

    # creating index
    time = pd.Series(meta['timeStep'] * np.array(xrange(0, len(data))))
    data['time'] = time

    data.set_index('time', inplace=True)

    # adding attributes
    data.units = units
    data.meta = meta
    data.date = meta['date']

    return data


def read_tweebot_data(file_name):
    """
    Reads dual-trap data and metadata from TweeBot datalog files.

    :param file_name: Path to the TweeBot datalog file.

    :return data: (pandas.DataFrame) contains redorded data and also meta data and units as attributes.

    .. note::

        Try things like data.units or data.meta to see what's available. Be
        aware that pandas.DataFrames can mutate when certain actions and
        computations are performed (for example shape changes). It's not clear
        whether the units and meta attributes persist.

    :return calibration: Dictionary containing the metadata of the experiment

    :return cal_units: Lookup Table for units of the calibration data

    Usage
    """"""
    >>> data = read_tweebot_txt('27.Datalog.2013.02.17.19.42.09.datalog.txt')

    .. note::

        This function so far only works for TweeBot data files in the form of 2013

    """
    # column_names, calibration, header_line = read_tweebot_data_header(file_name)
    HeaderInfo = read_tweebot_data_header(file_name)

    data = pd.read_table(file_name, header = HeaderInfo.header_pos)

    # get rid of unnamed and empty colums
    data = data.dropna(axis = 1)

    # add attributes from file_name
    FileInfo = parse_tweezer_file_name(file_name, parser='bot_data') 
    data.date = FileInfo.date
    data.trial = FileInfo.trial
    data.subtrial = FileInfo.subtrial

    # set column names and index as time 
    data.columns, data.units = simplify_tweebot_data_names(HeaderInfo.column_names)

    # determine timeStep as the smallest nearest-neighbour difference between sent times
    if 'timeSent' in data.columns:
        timeStep = min([round(n, 6) for n in np.diff(data.timeSent.values)])
    else:
        raise KeyError("Can't find *timeSent* column in the data frame...")

    data['time'] = np.float32(data.timeSent - min(data.timeSent))

    totalDuration = round(max(data.timeSent) - min(data.timeSent), 5)

    # creating time index frame
    time = pd.DataFrame({'time': np.float32(np.arange(0.00, totalDuration + timeStep, timeStep))})

    attributes = list(set(dir(data)) ^ set(dir(time)))

    combi = pd.merge(time, data, how='outer') 
    for a in attributes:
        combi.__setattr__(a, data.__getattribute__(a))

    # extracting meta data from calibration frame
    combi.meta = HeaderInfo.metadata
    combi.units.update(HeaderInfo.units)

    combi.meta['timeStep'] = timeStep

    return combi


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


def read_tweebot_data_header(datalog_file):
    """
    Extracts the header of a Tweebot data log file as a list

    :param datalog_file : (path) Tweebot datalog file from which the header is extracted

    :return HeaderInfo: (namedtuple) info container with fields 'column_names', 'metadata', 'units', and 'header_pos', 'data_pos'

    Usage:
    """"""
    >>> HeaderInfo = read_tweebot_data_header('27.Datalog.2013.02.17.19.42.09.datalog.txt')
    """
    with open(datalog_file, 'r') as f:
        fl = f.readlines(1000)

    # parsing header information
    comments = [line.strip().strip("# ") for line in fl[0:50] if line.strip().startswith('#')] 

    CommentInfo = extract_meta_and_units(comments)

    units = CommentInfo.units
    meta = CommentInfo.metadata

    meta['originalFile'] = datalog_file

    CommentInfo = extract_meta_and_units(comments)
    meta = CommentInfo.metadata
    units = CommentInfo.units

    # getting header and data
    header_pos = [ind for ind, line in enumerate(fl[0:45]) if re.match('^[a-zA-Z]', line.strip())][-1]
    header = fl[header_pos]
    column_names = [col.strip() for col in header.strip().split('\t')]

    data_pos = [ind for ind, line in enumerate(fl[0:45]) if re.match('^[-0-9]', line.strip())][0]

    HeaderInfo = namedtuple('HeaderInfo', ['column_names', 'metadata', 'units', 
        'header_pos', 'data_pos'])

    H = HeaderInfo(column_names, meta, units, header_pos, data_pos)

    return H


def gather_tweebot_data(trial=1, subtrial=None):
    pass

