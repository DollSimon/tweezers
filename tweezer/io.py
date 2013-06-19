"""
Input/Output routines for the tweezer package.

Performs file reads and data conversion.
"""
import re
from collections import namedtuple
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from pandas.core.datetools import Micro

import envoy
from nptdms import TdmsFile

from tweezer.tweebot.utils import simplify_tweebot_data_names
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
        names=columns, dtype=np.float64)

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

    .. warning::

        Currently this function removes duplicates in the *timeSent* column of the TweeBot datalog files.

    """
    # column_names, calibration, header_line = read_tweebot_data_header(file_name)
    HeaderInfo = read_tweebot_data_header(file_name)

    # _data = pd.read_table(file_name, header = HeaderInfo.header_pos, dtype=np.float64)
    try:
        _data = pd.read_csv(file_name, header = HeaderInfo.header_pos, sep='\t', dtype=np.float64)
    except:
        raise IOError("Can't read the file: {}".format(file_name))

    # get rid of unnamed and empty colums
    _data = _data.dropna(axis = 1)

    # add attributes from file_name
    FileInfo = parse_tweezer_file_name(file_name, parser='bot_data') 
    _data.date = FileInfo.date
    _data.trial = FileInfo.trial
    _data.subtrial = FileInfo.subtrial

    # set column names and index as time 
    _data.columns, _data.units = simplify_tweebot_data_names(HeaderInfo.column_names)

    # determine timeStep as the smallest nearest-neighbour difference between sent times
    if 'timeSent' in _data.columns:
        timeStep = Micro(1e6 * min([round(n, 6) for n in np.diff(_data.timeSent.values)]))
        if timeStep < Micro(1):
            try:
                timeStep = Micro(1e6 * HeaderInfo.metadata['deltaTime'])
            except:
                raise KeyError("Can't determine the timeStep for this file")

    else:
        raise KeyError("Can't determine the *timeStep* required for further calculations...")

    rounding_precision = int(abs(np.log10(timeStep.n / 1e6)) + 1)

    _data['relativeTime'] = np.float64(_data.timeSent) - round(min(_data.timeSent), 6)
    _data['time'] = [_data.date + timedelta(seconds=round(s, rounding_precision)) for s in _data.relativeTime.values]
    
    _data.drop_duplicates(cols='timeSent', inplace=True)

    _data.index = _data.time.values
    data = _data.asfreq(timeStep).drop(['time', 'relativeTime'], axis=1)

    # creating time index frame
    attributes = list(set(dir(data)) ^ set(dir(_data)))

    for a in attributes:
        data.__setattr__(a, _data.__getattribute__(a))

    # clean old frame
    del _data

    # extracting meta data from calibration frame
    data.meta = HeaderInfo.metadata
    data.units.update(HeaderInfo.units)

    data.meta['timeStep'] = timeStep

    return data


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
        date = datetime.strptime(date_string, '%m/%d/%Y %H:%M %p')
    except:
        date = datetime.now()

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
        names=columns, header=None, dtype=np.float64)

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
                date = datetime.strptime(date_string, '%m/%d/%Y %H:%M %p') 
            except:
                date = datetime.now()
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
        names=columns, header=None, dtype=np.float64)

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

    :return data: (pd.DataFrame) with the channels as columns and index based on file_name infos
    
    """
    info = parse_tweezer_file_name(file_name, parser='bot_tdms')

    # open tdms connection
    tf = TdmsFile(file_name)

    # read data
    if 'Untitled' in tf.groups():
        g = 'Untitled'
        data = pd.DataFrame(tf.channel_data(g, 'Untitled'), columns=['pmX'])
        data['pmY'] = tf.channel_data(g, 'Untitled 1')
        data['aodX'] = tf.channel_data(g, 'Untitled 2')
        data['aodY'] = tf.channel_data(g, 'Untitled 3')
        data['pmS'] = tf.channel_data(g, 'Untitled 4')
        data['aodS'] = tf.channel_data(g, 'Untitled 5')
        data['fbS'] = tf.channel_data(g, 'Untitled 6')
        data['mirrorX'] = tf.channel_data(g, 'Untitled 7')
        data['mirrorY'] = tf.channel_data(g, 'Untitled 8')
        data['fbX'] = tf.channel_data(g, 'Untitled 9')
        data['fbY'] = tf.channel_data(g, 'Untitled 10')
        data['pressure'] = tf.channel_data(g, 'Untitled 11')
        
    # setting the units
    units = {}
    units['pmY'] = 'V'
    units['aodX'] = 'V'
    units['aodY'] = 'V'
    units['pmS'] = 'V'
    units['aodS'] = 'V'
    units['fbS'] = 'V'
    units['mirrorX'] = 'V'
    units['mirrorY'] = 'V'
    units['fbX'] = 'V'
    units['fbY'] = 'V'
    units['pressure'] = 'V'

    # set index; in pandas the alias for microsecond offset is 'U'
    if info.date:
        index = pd.date_range(start = info.date, periods = len(data), freq = '{}U'.format(int(1000000.0/frequency)))
        data.index = index
        data.date = info.date
    else:
        index = pd.date_range(start = datetime.now(), periods = len(data), freq = '{}U'.format(int(1000000.0/frequency))  )
        data.index = index

    data.units = units

    return data 


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
    data = pd.read_csv(file_name, sep = '\t', dtype=np.float64)
    return data


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


def extract_meta_and_units(comment_list, file_type='man_data'):
    """
    Extracts metadata and units from the comments in raw tweezer data files

    :param comment_list: (list) List of strings that hold the raw comment lines

    :param file_type: (str) identifies the file type for which meta and units are extracted

    :return CommentInfo: (namedtuple) that holds dictionaries for metadata and units
    """
    units = {}
    meta = {}

    # set defaults
    units['laserDiodeCurrent'] = 'A'
    units['laserDiodeHours'] = 'h'
    units['laserDiodeTemp'] = 'C'
    units['viscosity'] = 'pN s / nm^2'

    units['samplingRate'] = 'Hz'
    units['recordingRate'] = 'Hz'
    units['timeStep'] = 's'

    units['aodDetectorOffsetX'] = 'V'
    units['aodDetectorOffsetY'] = 'V'
    units['pmDetectorOffsetX'] = 'V'
    units['pmDetectorOffsetY'] = 'V'

    units['pmDistanceConversionX'] = 'V/nm'
    units['pmDistanceConversionY'] = 'V/nm'
    units['aodDistanceConversionX'] = 'V/nm'
    units['aodDistanceConversionY'] = 'V/nm'

    units['pmDisplacementSensitivityX'] = 'V/nm'
    units['pmDisplacementSensitivityY'] = 'V/nm'
    units['aodDisplacementSensitivityX'] = 'V/nm'
    units['aodDisplacementSensitivityY'] = 'V/nm'

    units['pmStiffnessX'] = 'pN/nm'
    units['pmStiffnessY'] = 'pN/nm'
    units['aodStiffnessX'] = 'pN/nm'
    units['aodStiffnessY'] = 'pN/nm'

    units['pmBeadDiameter'] = 'nm'
    units['aodBeadDiameter'] = 'nm'
    units['pmBeadRadius'] = 'nm'
    units['aodBeadRadius'] = 'nm'

    units['laserDiodeTemp'] = 'C' 
    units['laserDiodeHours'] = 'h'
    units['laserDiodeCurrent'] = 'A'
    units['andorAodCenterX'] = 'px'
    units['andorAodCenterY'] = 'px'
    units['andorAodRangeX'] = 'px'
    units['andorAodRangeY'] = 'px'
    units['ccdAodCenterX'] = 'px'
    units['ccdAodCenterY'] = 'px'
    units['ccdAodRangeX'] = 'px'
    units['ccdAodRangeY'] = 'px'
    units['andorPmCenterX'] = 'px'
    units['andorPmCenterY'] = 'px'
    units['andorPmRangeX'] = 'px'
    units['andorPmRangeY'] = 'px'
    units['ccdPmCenterX'] = 'px'
    units['ccdPmCenterY'] = 'px'
    units['ccdPmRangeX'] = 'px'
    units['ccdPmRangeY'] = 'px'
    units['andorPixelSizeX'] = 'nm'
    units['andorPixelSizeY'] = 'nm'
    units['ccdPixelSizeX'] = 'nm'
    units['ccdPixelSizeY'] = 'nm'
    units['aodDetectorOffsetX'] = 'V'
    units['aodDetectorOffsetY'] = 'V'
    units['aodStiffnessX'] = 'pN/nm'
    units['aodStiffnessY'] = 'pN/nm'
    units['aodDistanceConversionX'] = 'V/nm'
    units['aodDistanceConversionY'] = 'V/nm'
    units['pmDetectorOffsetX'] = 'V'
    units['pmDetectorOffsetY'] = 'V'
    units['pmStiffnessX'] = 'pN/nm'
    units['pmStiffnessY'] = 'pN/nm'
    units['pmDistanceConversionX'] = 'V/nm'
    units['pmDistanceConversionY'] = 'V/nm'
    units['aodBeadRadius'] = 'nm'
    units['pmBeadRadius'] = 'nm'
    units['samplingRate'] = 'Hz'
    units['nSamples'] = 'int'
    units['deltaTime'] = 's'

    meta['laserDiodeCurrent'] = None
    meta['laserDiodeHours'] = None
    meta['laserDiodeTemp'] = None
    meta['viscosity'] = None

    meta['aodDetectorOffsetX'] = None
    meta['aodDetectorOffsetY'] = None
    meta['pmDetectorOffsetX'] = None
    meta['pmDetectorOffsetY'] = None

    meta['pmDistanceConversionX'] = None
    meta['pmDistanceConversionY'] = None
    meta['aodDistanceConversionX'] = None
    meta['aodDistanceConversionY'] = None

    meta['pmDisplacementSensitivityX'] = None
    meta['pmDisplacementSensitivityY'] = None
    meta['aodDisplacementSensitivityX'] = None
    meta['aodDisplacementSensitivityY'] = None

    meta['pmStiffnessX'] = None
    meta['pmStiffnessY'] = None
    meta['aodStiffnessX'] = None
    meta['aodStiffnessY'] = None

    meta['pmBeadDiameter'] = None
    meta['aodBeadDiameter'] = None
    meta['pmBeadRadius'] = None
    meta['pmBeadRadius'] = None

    meta['timeStep'] = None
    meta['samplingRate'] = None
    meta['recordingRate'] = None

    meta['andorAodCenterX'] = None
    meta['andorAodCenterY'] = None
    meta['andorAodRangeX'] = None
    meta['andorAodRangeY'] = None

    meta['ccdAodCenterX'] = None
    meta['ccdAodCenterY'] = None
    meta['ccdAodRangeX'] = None
    meta['ccdAodRangeY'] = None

    meta['andorPmCenterX'] = None
    meta['andorPmCenterY'] = None
    meta['andorPmRangeX'] = None
    meta['andorPmRangeY'] = None

    meta['ccdPmCenterX'] = None
    meta['ccdPmCenterY'] = None
    meta['ccdPmRangeX'] = None
    meta['ccdPmRangeY'] = None

    meta['andorPixelSizeX'] = None
    meta['andorPixelSizeY'] = None

    meta['ccdPixelSizeX'] = None
    meta['ccdPixelSizeY'] = None

    meta['samplingRate'] = None
    meta['nSamples'] = None
    meta['deltaTime'] = None

    for line in comment_list:
        if 'Date' in line:
            date_string = line.split(": ")[-1].replace("\t", " ")
        elif 'starttime' in line:
            time_string = line.strip().split(": ")[-1]
        elif 'Time of Experiment' in line:
            time_string = None
        elif 'Laser Diode Status' in line:
            pass
        elif 'thermal calibration' in line:
            pass
        elif 'data averaged to while-loop' in line:
            if 'FALSE' in line:
                isDataAveraged = False
            else:
                isDataAveraged = True

            meta['isDataAveraged'] = isDataAveraged

        elif 'errors' in line:
            error_string = line.split(": ")[-1]
            errors = [int(e) for e in error_string.split("\t")]
            if any(errors):
                hasErrors = True
            else:
                hasErrors = False

            meta['errors'] = errors
            meta['hasErrors'] = hasErrors

        elif 'number of samples' in line:
            try:
                nSamples = int(float(line.strip().split(": ")[-1]))
            except:
                nSamples = 1

            meta['nSamples'] = nSamples

        elif 'sample rate' in line:
            try:
                samplingRate = int(float(line.strip().split(": ")[-1]))
            except:
                samplingRate = 10000

            meta['samplingRate'] = samplingRate

        elif 'rate of while-loop' in line:
            try:
                recordingRate = int(float(line.strip().split(": ")[-1]))
            except:
                recordingRate = 10000

            meta['recordingRate'] = recordingRate

        elif 'duration of measurement' in line:
            try:
                duration = int(float(line.strip().split(": ")[-1]))
            except:
                duration = 0

            units['duration'] = 's'
            meta['duration'] = duration

        elif 'AOD detector horizontal offset' in line:
            try:
                aodDetectorOffsetX = float(line.strip().split(": ")[-1])
            except:
                aodDetectorOffsetX = 0

            units['aodDetectorOffsetX'] = 'V'
            meta['aodDetectorOffsetX'] = aodDetectorOffsetX

        elif 'AOD detector vertical offset' in line:
            try:
                aodDetectorOffsetY = float(line.strip().split(": ")[-1])
            except:
                aodDetectorOffsetY = 0

            units['aodDetectorOffsetY'] = 'V'
            meta['aodDetectorOffsetY'] = aodDetectorOffsetY

        elif 'PM detector horizontal offset' in line:
            try:
                pmDetectorOffsetX = float(line.strip().split(": ")[-1])
            except:
                pmDetectorOffsetX = 0

            units['pmDetectorOffsetX'] = 'V'
            meta['pmDetectorOffsetX'] = pmDetectorOffsetX

        elif 'PM detector vertical offset' in line:
            try:
                pmDetectorOffsetY = float(line.strip().split(": ")[-1])
            except:
                pmDetectorOffsetY = 0

            units['pmDetectorOffsetY'] = 'V'
            meta['pmDetectorOffsetY'] = pmDetectorOffsetY

        elif 'PM horizontal trap stiffness' in line:
            try:
                pmStiffnessX = float(line.strip().split(": ")[-1])
            except:
                pmStiffnessX = None

            meta['pmStiffnessX'] = pmStiffnessX

        elif 'PM vertical trap stiffness' in line:
            try:
                pmStiffnessY = float(line.strip().split(": ")[-1])
            except:
                pmStiffnessY = None

            meta['pmStiffnessY'] = pmStiffnessY
            
        elif 'AOD horizontal trap stiffness' in line:
            try:
                aodStiffnessX = float(line.strip().split(": ")[-1])
            except:
                aodStiffnessX = None

            meta['aodStiffnessX'] = aodStiffnessX
            
        elif 'AOD vertical trap stiffness' in line:
            try:
                aodStiffnessY = float(line.strip().split(": ")[-1])
            except:
                aodStiffnessY = None

            meta['aodStiffnessY'] = aodStiffnessY
            
        elif 'PM horizontal OLS' in line:
            try:
                pmDisplacementSensitivityX = float(line.strip().split(": ")[-1])
            except:
                pmDisplacementSensitivityX = None

            meta['pmDisplacementSensitivityX'] = pmDisplacementSensitivityX
            meta['pmDistanceConversionX'] = pmDisplacementSensitivityX
            
        elif 'PM vertical OLS' in line:
            try:
                pmDisplacementSensitivityY = float(line.strip().split(": ")[-1])
            except:
                pmDisplacementSensitivityY = None

            meta['pmDisplacementSensitivityY'] = pmDisplacementSensitivityY
            meta['pmDistanceConversionY'] = pmDisplacementSensitivityY
            
        elif 'AOD horizontal OLS' in line:
            try:
                aodDisplacementSensitivityX = float(line.strip().split(": ")[-1])
            except:
                aodDisplacementSensitivityX = None

            meta['aodDisplacementSensitivityX'] = aodDisplacementSensitivityX
            meta['aodDistanceConversionX'] = aodDisplacementSensitivityX
            
        elif 'AOD vertical OLS' in line:
            try:
                aodDisplacementSensitivityY = float(line.strip().split(": ")[-1])
            except:
                aodDisplacementSensitivityY = None

            meta['aodDisplacementSensitivityY'] = aodDisplacementSensitivityY
            meta['aodDistanceConversionY'] = aodDisplacementSensitivityY
            
        elif 'Viscosity' in line:
            try:
                viscosity = float(line.strip().split(": ")[-1])
            except:
                viscosity = 0.8902e-9 # viscosity of water @ 25C

            units['viscosity'] = 'pN s / nm^2'
            meta['viscosity'] = viscosity

        elif 'dt ' in line:
            try:
                dt = float(line.strip().split(": ")[-1])
            except:
                dt = 0.0010

            units['dt'] = units['timeStep'] = 's'
            meta['dt'] = meta['timeStep'] = dt 

        elif 'PM bead diameter' in line:
            try:
                pmBeadDiameter = float(line.strip().split(": ")[-1])
                if pmBeadDiameter < 20:
                    pmBeadDiameter = pmBeadDiameter * 1000
                elif '(um)' in line:
                    pmBeadDiameter = pmBeadDiameter * 1000
            except:
                pmBeadDiameter = 0

            pmBeadRadius = pmBeadDiameter / 2.0

            meta['pmBeadDiameter'] = pmBeadDiameter
            meta['pmBeadRadius'] = pmBeadRadius

        elif 'AOD bead diameter' in line:
            try:
                aodBeadDiameter = float(line.strip().split(": ")[-1])
                if aodBeadDiameter < 20:
                    aodBeadDiameter = aodBeadDiameter * 1000
                elif '(um)' in line:
                    aodBeadDiameter = aodBeadDiameter * 1000
            except:
                aodBeadDiameter = 0

            aodBeadRadius = aodBeadDiameter / 2.0

            meta['aodBeadDiameter'] = aodBeadDiameter
            meta['aodBeadRadius'] = aodBeadRadius

        elif 'Laser Diode Temp' in line:
            laserDiodeTemp = float(line.strip().split(": ")[-1])
            meta['laserDiodeTemp'] = laserDiodeTemp

        elif 'Laser Diode Operating Hours' in line:
            laserDiodeHours = float(line.strip().split(": ")[-1])
            meta['laserDiodeHours'] = laserDiodeHours

        elif 'Laser Diode Current' in line:
            laserDiodeCurrent = float(line.strip().split(": ")[-1])
            meta['laserDiodeCurrent'] = laserDiodeCurrent

        elif 'AOD ANDOR center x' in line:
            andorAodCenterX = float(line.strip().split(": ")[-1])
            meta['andorAodCenterX'] = andorAodCenterX

        elif 'AOD ANDOR center y' in line:
            andorAodCenterY = float(line.strip().split(": ")[-1])
            meta['andorAodCenterY'] = andorAodCenterY

        elif 'AOD ANDOR range x' in line:
            andorAodRangeX = float(line.strip().split(": ")[-1])
            meta['andorAodRangeX'] = andorAodRangeX

        elif 'AOD ANDOR range y' in line:
            andorAodRangeY = float(line.strip().split(": ")[-1])
            meta['andorAodRangeY'] = andorAodRangeY

        elif 'AOD CCD center x' in line:
            ccdAodCenterX = float(line.strip().split(": ")[-1])
            meta['ccdAodCenterX'] = ccdAodCenterX

        elif 'AOD CCD center y' in line:
            ccdAodCenterY = float(line.strip().split(": ")[-1])
            meta['ccdAodCenterY'] = ccdAodCenterY

        elif 'AOD CCD range x' in line:
            ccdAodRangeX = float(line.strip().split(": ")[-1])
            meta['ccdAodRangeX'] = ccdAodRangeX

        elif 'AOD CCD range y' in line:
            ccdAodRangeY = float(line.strip().split(": ")[-1])
            meta['ccdAodRangeY'] = ccdAodRangeY

        elif 'PM ANDOR center x' in line:
            andorPmCenterX = float(line.strip().split(": ")[-1])
            meta['andorPmCenterX'] = andorPmCenterX

        elif 'PM ANDOR center y' in line:
            andorPmCenterY = float(line.strip().split(": ")[-1])
            meta['andorPmCenterY'] = andorPmCenterY

        elif 'PM ANDOR range x' in line:
            andorPmRangeX = float(line.strip().split(": ")[-1])
            meta['andorPmRangeX'] = andorPmRangeX

        elif 'PM ANDOR range y' in line:
            andorPmRangeY = float(line.strip().split(": ")[-1])
            meta['andorPmRangeY'] = andorPmRangeY

        elif 'PM CCD center x' in line:
            ccdPmCenterX = float(line.strip().split(": ")[-1])
            meta['ccdPmCenterX'] = ccdPmCenterX

        elif 'PM CCD center y' in line:
            ccdPmCenterY = float(line.strip().split(": ")[-1])
            meta['ccdPmCenterY'] = ccdPmCenterY

        elif 'PM CCD range x' in line:
            ccdPmRangeX = float(line.strip().split(": ")[-1])
            meta['ccdPmRangeX'] = ccdPmRangeX

        elif 'PM CCD range y' in line:
            ccdPmRangeY = float(line.strip().split(": ")[-1])
            meta['ccdPmRangeY'] = ccdPmRangeY

        elif 'ANDOR pixel size x' in line:
            andorPixelSizeX = float(line.strip().split(": ")[-1])
            meta['andorPixelSizeX'] = andorPixelSizeX

        elif 'ANDOR pixel size y' in line:
            andorPixelSizeY = float(line.strip().split(": ")[-1])
            meta['andorPixelSizeY'] = andorPixelSizeY

        elif 'CCD pixel size x' in line:
            ccdPixelSizeX = float(line.strip().split(": ")[-1])
            meta['ccdPixelSizeX'] = ccdPixelSizeX

        elif 'CCD pixel size y' in line:
            ccdPixelSizeY = float(line.strip().split(": ")[-1])
            meta['ccdPixelSizeY'] = ccdPixelSizeY

        elif 'AOD detector x offset' in line:
            aodDetectorOffsetX = float(line.strip().split(": ")[-1])
            meta['aodDetectorOffsetX'] = aodDetectorOffsetX

        elif 'AOD detector y offset' in line:
            aodDetectorOffsetY = float(line.strip().split(": ")[-1])
            meta['aodDetectorOffsetY'] = aodDetectorOffsetY

        elif 'AOD trap stiffness x' in line:
            aodStiffnessX = float(line.strip().split(": ")[-1])
            meta['aodStiffnessX'] = aodStiffnessX

        elif 'AOD trap stiffness y' in line:
            aodStiffnessY = float(line.strip().split(": ")[-1])
            meta['aodStiffnessY'] = aodStiffnessY

        elif 'AOD trap distance conversion x' in line:
            aodDistanceConversionX = float(line.strip().split(": ")[-1])
            meta['aodDistanceConversionX'] = aodDistanceConversionX

        elif 'AOD trap distance conversion y' in line:
            aodDistanceConversionY = float(line.strip().split(": ")[-1])
            meta['aodDistanceConversionY'] = aodDistanceConversionY

        elif 'PM detector x offset' in line:
            pmDetectorOffsetX = float(line.strip().split(": ")[-1])
            meta['pmDetectorOffsetX'] = pmDetectorOffsetX

        elif 'PM detector y offset' in line:
            pmDetectorOffsetY = float(line.strip().split(": ")[-1])
            meta['pmDetectorOffsetY'] = pmDetectorOffsetY

        elif 'PM trap stiffness x' in line:
            pmStiffnessX = float(line.strip().split(": ")[-1])
            meta['pmStiffnessX'] = pmStiffnessX

        elif 'PM trap stiffness y' in line:
            pmStiffnessY = float(line.strip().split(": ")[-1])
            meta['pmStiffnessY'] = pmStiffnessY

        elif 'PM trap distance conversion x' in line:
            pmDistanceConversionX = float(line.strip().split(": ")[-1])
            meta['pmDistanceConversionX'] = pmDistanceConversionX

        elif 'PM trap distance conversion y' in line:
            pmDistanceConversionY = float(line.strip().split(": ")[-1])
            meta['pmDistanceConversionY'] = pmDistanceConversionY

        elif 'AOD bead radius' in line:
            try:
                aodBeadRadius = float(line.strip().split(": ")[-1])
                if aodBeadRadius < 20:
                    aodBeadRadius = aodBeadRadius * 1000
                elif '(um)' in line:
                    aodBeadRadius = aodBeadRadius * 1000
            except:
                aodBeadRadius = 0

            aodBeadDiameter = 2.0 * aodBeadRadius

            meta['aodBeadDiameter'] = round(aodBeadDiameter, 2)
            meta['aodBeadRadius'] = round(aodBeadRadius, 2)

        elif 'PM bead radius ' in line:
            try:
                pmBeadRadius = float(line.strip().split(": ")[-1])
                if pmBeadRadius < 20:
                    pmBeadRadius = pmBeadRadius * 1000
                elif '(um)' in line:
                    pmBeadRadius = pmBeadRadius * 1000
            except:
                pmBeadRadius = 0

            pmBeadDiameter = 2.0 * pmBeadRadius

            meta['pmBeadDiameter'] = round(pmBeadDiameter, 2)
            meta['pmBeadRadius'] = round(pmBeadRadius, 2)

        elif 'Sample rate' in line:
            samplingRate = float(line.strip().split(": ")[-1])
            meta['samplingRate'] = samplingRate

        elif 'Number of samples' in line:
            nSamples = float(line.strip().split(": ")[-1])
            meta['nSamples'] = nSamples

        elif 'Delta time' in line:
            deltaTime = float(line.strip().split(": ")[-1])
            meta['deltaTime'] = deltaTime

        elif 'Laser Diode Operating Hours' in line:
            try:
                laserDiodeHours = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeHours = 0

            meta['laserDiodeHours'] = laserDiodeHours
            units['laserDiodeHours'] = 'h'

        elif 'Laser Diode Current' in line:
            try:
                laserDiodeCurrent = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeCurrent = 0

            meta['laserDiodeCurrent'] = laserDiodeCurrent
            units['laserDiodeCurrent'] = 'A'

        elif 'Laser Diode Temp' in line:
            try:
                laserDiodeTemp = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeTemp = 0

            meta['laserDiodeTemp'] = laserDiodeTemp
            units['laserDiodeTemp'] = 'C'

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
            meta[var] = value

    # parsing the date
    if date_string and time_string:
        combined_date = " ".join([date_string.strip(), time_string.strip()])
        date = datetime.datetime.strptime(combined_date, '%m/%d/%Y %I:%M %p')
    else:
        date = datetime.datetime.now()

    meta['date'] = date

    CommentInfo = namedtuple('CommentInfo', ['metadata', 'units'])
    C = CommentInfo(meta, units)
