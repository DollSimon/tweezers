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

from tweezer.bot.utils import simplify_tweebot_data_names
from tweezer.core.parsers import parse_tweezer_file_name

try:
    from PIL import Image
except ImportError:
    print('Somehow PIL could not be imported correctly...')
    raise


def read_tweezer_txt(fileName):
    """
    Reads dual-trap data and metadata contained in text files.

    :param str fileName: the full path to the data file to read
    :returns: (:class:`pandas.DataFrame`) experiment data
    """

    # check file sanity and correct it if necessary
    shell_call = envoy.run('tail -n 12 {}'.format(fileName), timeout=5)
    if shell_call.status_code is 0:
        tail = shell_call.std_out.split("\n")
    else:
        raise IOError("The file {} does not exist".format(fileName))

    if any([l.strip().startswith("#") for l in tail]):
        isFileSane = False
    else:
        isFileSane = True

    with open(fileName, 'r', encoding='utf-8') as f:
        fl = []
        for i in range(60):
            fl.append(f.readline())

    # parsing header information
    headerComments = [line.strip().strip("# ") for line in fl[0:40] if line.strip().startswith('#')]
    tailComments = [line.strip().strip("# ") for line in tail[-10:] if line.strip().startswith('#')]
    comments = headerComments + tailComments

    CommentInfo = extract_meta_and_units(comments)

    units = CommentInfo.units
    meta = CommentInfo.metadata

    meta['originalFile'] = fileName
    meta['isFileSane'] = isFileSane

    # getting header and data
    headerIndices = [ind for ind, line in enumerate(fl[0:45]) if re.match(r'^[a-zA-Z]', line.strip())][-1]
    header = fl[headerIndices]
    columnPrecursor = [col.strip() for col in header.strip().split('\t')]

    columns = []
    for c in columnPrecursor:
        if re.search(r'\(([a-zA-Z]+)\)', c):
            name, unit = re.search(r'^(\w+)\s+\(([a-zA-Z]+)\)', c).groups()
            columns.append(name)
            units[name] = unit
        else:
            columns.append(c)

    firstDataLine = [ind for ind, line in enumerate(fl[0:45]) if re.match(r'^[-0-9]', line.strip())][0]

    if isFileSane:
        data = pd.read_table(fileName, sep='\t', header=None, skiprows=firstDataLine,
            names=columns, dtype=np.float64)
    else:
        data = pd.read_table(fileName, sep='\t', header=None, skiprows=firstDataLine,
            skipfooter=10, names=columns, dtype=np.float64)

    # drop rows with "NaN" values
    data = data.dropna()

    # creating index
    time = pd.Series(meta['timeStep'] * np.array(range(0, len(data))))
    data['time'] = time

    data.set_index('time', inplace=True)

    # adding attributes
    data.units = units
    data.meta = meta
    data.date = meta['date']

    return data


def read_tweebot_data(fileName):
    """
    Reads dual-trap data and metadata from TweeBot datalog files.

    :param str fileName: path to the TweeBot datalog file

    :returns data: (:class:`pandas.DataFrame`) contains recorded data and also meta \
    data and units as attributes.

    .. note::

        Test things like 'data.units' or data.meta to see what's available. Be
        aware that :class:`pandas.DataFrame` can mutate when certain actions and
        computations are performed (for example shape changes). It's not clear
        whether the units and meta attributes persist.

    :returns: * **calibration** (:class:`dict`) -- metadata of the experiment
              * **cal_units** (:class:`dict`) -- lookup Table for units of the calibration data

    Usage:

    >>> data = read_tweebot_txt('27.Datalog.2013.02.17.19.42.09.datalog.txt')

    .. note::

        This function so far only works for TweeBot data files in the form of \
        2013

    .. warning::

        Currently this function removes duplicates in the *timeSent* column \
        of the TweeBot datalog files.

    """

    # columnNames, calibration, header = read_tweebot_data_header(fileName)
    HeaderInfo = read_tweebot_data_header(fileName)

    try:
        _data = pd.read_csv(fileName,
                            header=HeaderInfo.headerIndices,
                            sep='\t',
                            dtype=np.float64)
    except:
        raise IOError("Can't read the file: {}".format(fileName))

    # get rid of unnamed and empty colums
    _data = _data.dropna(axis=1)

    # add attributes from fileName
    FileInfo = parse_tweezer_file_name(fileName, parser='bot_data')
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
    data.meta['original_file'] = fileName

    return data


def read_thermal_calibration(fileName, frequency=80000):
    """
    Reads time series and calculated power spectra of a thermal calibration.

    :param str fileName: path to the tweezer time series file containing the raw values of the PSD signals

    :param int frequency: sampling frequency of time series

    :returns: (:class:`pandas.DataFrame`) raw thermal calibration data with time as index

    """
    # get header information
    with open(fileName, 'r', encoding='utf-8') as f:
        fl = []
        for i in range(60):
            fl.append(f.readline())

    # finding the date; if any error occurs take the current date and time
    comments = [line for line in fl[0:15] if line.strip().startswith('#')]

    try:
        dateString = [l.strip().replace("\t", " ").split(": ")[-1] for l in comments if 'Date' in l][0]
        date = datetime.strptime(dateString, '%m/%d/%Y %H:%M %p')
    except:
        date = datetime.now()

    try:
        nSamples = int(float([l.strip().split(": ")[-1] for l in comments if 'samples' in l][0]))
    except:
        nSamples = 2**20

    # time step in seconds
    dt = 1.0/frequency
    time = [dt*i for i in range(nSamples)]

    # read header information
    headerIndices = [ind for ind, line in enumerate(fl[0:15]) if re.match(r'^[a-zA-Z]', line.strip())][-1]
    header = fl[headerIndices]
    columns = [col.replace('.', '_').strip() for col in header.strip().split('\t')]

    firstDataLine = [ind for ind, line in enumerate(fl[0:45]) if re.match(r'^[-0-9]', line.strip())][0]

    # read file data
    ts = pd.read_table(fileName, sep='\t', skiprows=firstDataLine,
                       names=columns, header=None, dtype=np.float64)

    # setting time as a data column and an index to be on the safe side
    ts['time'] = time
    ts.index = time

    # pass date as an attribute
    ts.date = date
    ts.nSamples = nSamples

    return ts


def read_tweezer_power_spectrum(fileName):
    """
    Reads data from tweezer power spectrum file. These files are produced by LabView and contain the raw PSDs and the \
    fits used to extract trap calibration results.

    :param str fileName: file path to the tweezer power spectrum file

    :returns: (:class:`pandas.DataFrame`) all the raw and fitted data as well as the fit results
    """
    # get header information
    with open(fileName, 'r', encoding='utf-8') as f:
        fl = []
        for i in range(60):
            fl.append(f.readline())

    # parsing header information
    comments = [line.strip().strip("#").strip() for line in fl[0:40] if line.strip().startswith('#')]

    CommentInfo = extract_meta_and_units(comments)

    # getting header and data
    headerIndices = [ind for ind, line in enumerate(fl[0:45]) if re.match(r'^[a-zA-Z]', line.strip())][-1]
    header = fl[headerIndices]
    columns = [col.replace('.', '_').strip() for col in header.strip().split('\t')]

    firstDataLine = [ind for ind, line in enumerate(fl[0:45]) if re.match(r'^[-0-9]', line.strip())][0]

    # read file data
    psd = pd.read_table(fileName, sep='\t', skiprows=firstDataLine,
        names=columns, header=None, dtype=np.float64)

    for k, v in CommentInfo.metadata.items():
        try:
            psd.__setattr__(str(k), v)
        except TypeError as err:
            print(err)
            raise

    psd.units = CommentInfo.units

    return psd


def read_distance_calibration_data(comments):
    """
    Extract fit and l

    :param input: Description
    """
    pass


def read_tdms(fileName, frequency=1000):
    """
    Reads data from Labview TDMS file.

    :param str fileName: path to tdms file

    :param int frequency: sampling frequency in Hz (default 1000, i.e. data taken at 1 ms time resolution)

    :returns: (:class:`pandas.DataFrame`) channels as columns and index based on fileName infos

    """
    info = parse_tweezer_file_name(fileName, parser='bot_tdms')

    # open tdms connection
    tf = TdmsFile(fileName)

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


def read_tweebot_stats(fileName):
    """
    Reads data from TweeBot statistic files.
    """
    pass


def read_tweebot_logs(fileName):
    """
    Reads data from TweeBot log files.

    :param str fileName: path to Tweebot log file to be parsed

    :returns: (:class:`pandas.DataFrame`) logging data
    """
    log = pd.read_table(fileName)
    log.columns = ['time', 'kind', 'routine', 'message']
    log.index = pd.to_datetime(log.time)
    log.tz_localize('Europe/Berlin')
    log.drop('time', axis=1)

    return log


def read_tracking_data(fileName):
    """
    Reads data from Tweezer Tracking files.

    :param str fileName: path to the tweezer tracking file
    :returns: (:class:`pandas.DataFrame`) data
    """
    data = pd.read_csv(fileName, sep = '\t', dtype=np.float64)
    return data


def read_tweebot_data_header(datalog_file):
    """
    Extracts the header of a Tweebot data log file as a list

    :param str datalog_file: path to Tweebot datalog file from which the header is extracted

    :returns: (:func:`collections.namedtuple`) info container with fields 'column_names', 'metadata', 'units',
    and 'headerIndices', 'firstDataLine'

    Usage:

    >>> HeaderInfo = read_tweebot_data_header('27.Datalog.2013.02.17.19.42.09.datalog.txt')
    """
    # get header information
    with open(datalog_file, 'r', encoding='utf-8') as f:
        fl = []
        for i in range(60):
            fl.append(f.readline())

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
    headerIndices = [ind for ind, line in enumerate(fl[0:45]) if re.match(r'^[a-zA-Z]', line.strip())][-1]
    header = fl[headerIndices]
    column_names = [col.strip() for col in header.strip().split('\t')]

    firstDataLine = [ind for ind, line in enumerate(fl[0:45]) if re.match(r'^[-0-9]', line.strip())][0]

    HeaderInfo = namedtuple('HeaderInfo', ['column_names', 'metadata', 'units',
        'headerIndices', 'firstDataLine'])

    H = HeaderInfo(column_names, meta, units, headerIndices, firstDataLine)

    return H


def read_tweezer_image_info(fileName, fileType='man_pics'):
    """
    Extracts basic information about an image.

    :param str fileName: path to the image
    :param str fileType: ? (optional, default 'man_pics')

    :return: description
    """
    try:
        im = Image.open(fileName)
    except IOError:
        print('Could not open the image {}'.format(fileName))
        raise

    info = {}
    info['original_file'] = fileName
    info['file_type'] = fileType
    info['file_type'] = 'image'
    info['size'] = im.size
    info['format'] = im.format
    try:
        info['FileInfo'] = parse_tweezer_file_name(fileName, parser=fileType)
    except:
        print('Could not extract file information from the file name.')

    return info


def gather_tweebot_data(trial=1, subtrial=None):
    pass


def extract_meta_and_units(comment_list, file_type='man_data'):
    """
    Extracts metadata and units from the comments in raw tweezer data files.

    :param list comment_list: list of strings that hold the raw comment lines

    :param str file_type: identifies the file type for which meta and units are extracted

    :returns: (:func:`collections.namedtuple`) that holds dictionaries for metadata and units
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

    time_string = None

    for line in comment_list:
        if 'Date' in line:
            dateString = line.split(": ")[-1].replace("\t", " ")
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

            meta[standardized_name_of('data averaged to while-loop')] = isDataAveraged

        elif 'errors' in line:
            error_string = line.split(": ")[-1]
            errors = [int(e) for e in error_string.split("\t")]
            if any(errors):
                hasErrors = True
            else:
                hasErrors = False

            meta['errors'] = errors
            meta['hasErrors'] = hasErrors

        elif 'number of samples' in line or 'nSamples' in line:
            try:
                nSamples = int(float(line.strip().split(": ")[-1]))
            except:
                nSamples = 1

            meta[standardized_name_of('nSamples')] = nSamples

        elif 'sample rate' in line or 'sampleRate.Hz' in line:
            try:
                match = re.search('(sample\srate|sampleRate\.Hz)\s*\.*[:\s]+(\d+\.*\d*)', line)
                samplingRate = int(float(match.group(2)))
            except:
                samplingRate = 10000

            meta[standardized_name_of('sample rate')] = samplingRate
            units[standardized_name_of('sample rate')] = standardized_unit_of('sample rate')

        elif 'rate of while-loop' in line:
            try:
                recordingRate = int(float(line.strip().split(": ")[-1]))
            except:
                recordingRate = 10000

            meta[standardized_name_of('rate of while-loop')] = recordingRate

        elif 'duration of measurement' in line:
            try:
                duration = int(float(line.strip().split(": ")[-1]))
            except:
                duration = 0

            units['duration'] = 's'
            meta['duration'] = duration

        elif 'AOD detector horizontal offset' in line or 'xOffsetT2' in line:
            try:
                aodDetectorOffsetX = float(line.strip().split(": ")[-1])
            except:
                aodDetectorOffsetX = 0

            meta[standardized_name_of('AOD detector horizontal offset')] = aodDetectorOffsetX
            units[standardized_name_of('AOD detector horizontal offset')] = standardized_unit_of('AOD detector horizontal offset')

        elif 'AOD detector vertical offset' in line or 'yOffsetT2' in line:
            try:
                aodDetectorOffsetY = float(line.strip().split(": ")[-1])
            except:
                aodDetectorOffsetY = 0

            meta[standardized_name_of('AOD detector vertical offset')] = aodDetectorOffsetY
            units[standardized_name_of('AOD detector vertical offset')] = standardized_unit_of('AOD detector vertical offset')

        elif 'PM detector horizontal offset' in line or 'xOffsetT1' in line:
            try:
                pmDetectorOffsetX = float(line.strip().split(": ")[-1])
            except:
                pmDetectorOffsetX = 0

            meta[standardized_name_of('PM detector horizontal offset')] = pmDetectorOffsetX
            units[standardized_name_of('PM detector horizontal offset')] = standardized_unit_of('PM detector horizontal offset')

        elif 'PM detector vertical offset' in line or 'yOffsetT1' in line:
            try:
                pmDetectorOffsetY = float(line.strip().split(": ")[-1])
            except:
                pmDetectorOffsetY = 0

            meta[standardized_name_of('PM detector vertical offset')] = pmDetectorOffsetY
            units[standardized_name_of('PM detector vertical offset')] = standardized_unit_of('PM detector vertical offset')

        elif 'PM horizontal trap stiffness' in line or 'xStiffnessT1' in line:
            try:
                pmStiffnessX = float(line.strip().split(": ")[-1])
            except:
                pmStiffnessX = None

            meta[standardized_name_of('PM horizontal trap stiffness')] = pmStiffnessX
            units[standardized_name_of('PM horizontal trap stiffness')] = standardized_unit_of('PM horizontal trap stiffness')

        elif 'PM vertical trap stiffness' in line or 'yStiffnessT1' in line:
            try:
                pmStiffnessY = float(line.strip().split(": ")[-1])
            except:
                pmStiffnessY = None

            meta[standardized_name_of('PM vertical trap stiffness')] = pmStiffnessY
            units[standardized_name_of('PM vertical trap stiffness')] = standardized_unit_of('PM vertical trap stiffness')

        elif 'AOD horizontal trap stiffness' in line or 'xStiffnessT2' in line:
            try:
                aodStiffnessX = float(line.strip().split(": ")[-1])
            except:
                aodStiffnessX = None

            meta[standardized_name_of('AOD horizontal trap stiffness')] = aodStiffnessX
            units[standardized_name_of('AOD horizontal trap stiffness')] = standardized_unit_of('AOD horizontal trap stiffness')

        elif 'AOD vertical trap stiffness' in line or 'yStiffnessT2' in line:
            try:
                aodStiffnessY = float(line.strip().split(": ")[-1])
            except:
                aodStiffnessY = None

            meta[standardized_name_of('AOD vertical trap stiffness')] = aodStiffnessY
            units[standardized_name_of('AOD vertical trap stiffness')] = standardized_unit_of('AOD vertical trap stiffness')

        elif 'PM horizontal OLS' in line or 'xDistConversionT1' in line:
            try:
                pmDisplacementSensitivityX = float(line.strip().split(": ")[-1])
            except:
                pmDisplacementSensitivityX = None

            meta[standardized_name_of('PM horizontal OLS')] = pmDisplacementSensitivityX
            units[standardized_name_of('PM horizontal OLS')] = standardized_unit_of('PM horizontal OLS')

        elif 'PM vertical OLS' in line or 'yDistConversionT1' in line:
            try:
                pmDisplacementSensitivityY = float(line.strip().split(": ")[-1])
            except:
                pmDisplacementSensitivityY = None

            meta[standardized_name_of('PM vertical OLS')] = pmDisplacementSensitivityY
            meta[standardized_name_of('PM vertical OLS')] = pmDisplacementSensitivityY

        elif 'AOD horizontal OLS' in line or 'xDistConversionT2' in line:
            try:
                aodDisplacementSensitivityX = float(line.strip().split(": ")[-1])
            except:
                aodDisplacementSensitivityX = None

            meta[standardized_name_of('AOD horizontal OLS')] = aodDisplacementSensitivityX
            meta[standardized_name_of('AOD horizontal OLS')] = aodDisplacementSensitivityX

        elif 'AOD vertical OLS' in line or 'yDistConversionT2' in line:
            try:
                aodDisplacementSensitivityY = float(line.strip().split(": ")[-1])
            except:
                aodDisplacementSensitivityY = None

            meta[standardized_name_of('AOD vertical OLS')] = aodDisplacementSensitivityY
            meta[standardized_name_of('AOD vertical OLS')] = aodDisplacementSensitivityY

        elif 'Viscosity' in line or 'viscosity' in line:
            try:
                viscosity = float(line.strip().split(": ")[-1])
            except:
                viscosity = 0.8902e-9 # viscosity of water @ 25C

            units['viscosity'] = 'pN s / nm^2'
            meta[standardized_name_of('viscosity')] = viscosity

        elif 'dt ' in line:
            try:
                dt = float(line.strip().split(": ")[-1])
            except:
                dt = 0.0010

            units['dt'] = units['timeStep'] = 's'
            meta[standardized_name_of('dt')] = meta[standardized_name_of('timeStep')] = dt

        elif 'Delta time ' in line:
            try:
                dt = float(line.strip().split(": ")[-1])
            except:
                dt = 0.0010

            meta[standardized_name_of('Delta time')] = dt

        elif 'PM bead diameter' in line or 'diameterT1.um' in line:
            try:
                pmBeadDiameter = float(line.strip().split(": ")[-1])
                if pmBeadDiameter < 20:
                    pmBeadDiameter = pmBeadDiameter * 1000
                elif '(um)' in line:
                    pmBeadDiameter = pmBeadDiameter * 1000
            except:
                pmBeadDiameter = 0

            pmBeadRadius = pmBeadDiameter / 2.0

            meta[standardized_name_of('PM bead diameter')] = pmBeadDiameter
            meta[standardized_name_of('PM bead radius')] = pmBeadRadius

        elif 'AOD bead diameter' in line or 'diameterT2.um' in line:
            try:
                aodBeadDiameter = float(line.strip().split(": ")[-1])
                if aodBeadDiameter < 20:
                    aodBeadDiameter = aodBeadDiameter * 1000
                elif '(um)' in line:
                    aodBeadDiameter = aodBeadDiameter * 1000
            except:
                aodBeadDiameter = 0

            aodBeadRadius = aodBeadDiameter / 2.0

            meta[standardized_name_of('AOD bead diameter')] = aodBeadDiameter
            meta[standardized_name_of('AOD bead radius')] = aodBeadRadius

        elif 'Laser Diode Temp' in line:
            laserDiodeTemp = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('Laser Diode Temp')] = laserDiodeTemp

        elif 'Laser Diode Operating Hours' in line:
            laserDiodeHours = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('Laser Diode Operating Hours')] = laserDiodeHours

        elif 'Laser Diode Current' in line:
            laserDiodeCurrent = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('Laser Diode Current')] = laserDiodeCurrent

        elif 'AOD ANDOR center x' in line:
            andorAodCenterX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD ANDOR center x')] = andorAodCenterX

        elif 'AOD ANDOR center y' in line:
            andorAodCenterY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD ANDOR center y')] = andorAodCenterY

        elif 'AOD ANDOR range x' in line:
            andorAodRangeX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD ANDOR range x')] = andorAodRangeX

        elif 'AOD ANDOR range y' in line:
            andorAodRangeY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD ANDOR range y')] = andorAodRangeY

        elif 'AOD CCD center x' in line:
            ccdAodCenterX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD CCD center x')] = ccdAodCenterX

        elif 'AOD CCD center y' in line:
            ccdAodCenterY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD CCD center y')] = ccdAodCenterY

        elif 'AOD CCD range x' in line:
            ccdAodRangeX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD CCD range x')] = ccdAodRangeX

        elif 'AOD CCD range y' in line:
            ccdAodRangeY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD CCD range y')] = ccdAodRangeY

        elif 'PM ANDOR center x' in line:
            andorPmCenterX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM ANDOR center x')] = andorPmCenterX

        elif 'PM ANDOR center y' in line:
            andorPmCenterY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM ANDOR center y')] = andorPmCenterY

        elif 'PM ANDOR range x' in line:
            andorPmRangeX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM ANDOR range x')] = andorPmRangeX

        elif 'PM ANDOR range y' in line:
            andorPmRangeY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM ANDOR range y')] = andorPmRangeY

        elif 'PM CCD center x' in line:
            ccdPmCenterX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM CCD center x')] = ccdPmCenterX

        elif 'PM CCD center y' in line:
            ccdPmCenterY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM CCD center y')] = ccdPmCenterY

        elif 'PM CCD range x' in line:
            ccdPmRangeX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM CCD range x')] = ccdPmRangeX

        elif 'PM CCD range y' in line:
            ccdPmRangeY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM CCD range y')] = ccdPmRangeY

        elif 'ANDOR pixel size x' in line:
            andorPixelSizeX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('ANDOR pixel size x')] = andorPixelSizeX

        elif 'ANDOR pixel size y' in line:
            andorPixelSizeY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('ANDOR pixel size y')] = andorPixelSizeY

        elif 'CCD pixel size x' in line:
            ccdPixelSizeX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('CCD pixel size x')] = ccdPixelSizeX

        elif 'CCD pixel size y' in line:
            ccdPixelSizeY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('CCD pixel size y')] = ccdPixelSizeY

        elif 'AOD detector x offset' in line:
            aodDetectorOffsetX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD detector x offset')] = aodDetectorOffsetX

        elif 'AOD detector y offset' in line:
            aodDetectorOffsetY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD detector y offset')] = aodDetectorOffsetY

        elif 'AOD trap stiffness x' in line:
            aodStiffnessX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD trap stiffness x')] = aodStiffnessX

        elif 'AOD trap stiffness y' in line:
            aodStiffnessY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD trap stiffness y')] = aodStiffnessY

        elif 'AOD trap distance conversion x' in line:
            aodDistanceConversionX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD trap distance conversion x')] = aodDistanceConversionX

        elif 'AOD trap distance conversion y' in line:
            aodDistanceConversionY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('AOD trap distance conversion y')] = aodDistanceConversionY

        elif 'PM detector x offset' in line:
            pmDetectorOffsetX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM detector x offset')] = pmDetectorOffsetX

        elif 'PM detector y offset' in line:
            pmDetectorOffsetY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM detector y offset')] = pmDetectorOffsetY

        elif 'PM trap stiffness x' in line:
            pmStiffnessX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM trap stiffness x')] = pmStiffnessX

        elif 'PM trap stiffness y' in line:
            pmStiffnessY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM trap stiffness y')] = pmStiffnessY

        elif 'PM trap distance conversion x' in line:
            pmDistanceConversionX = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM trap distance conversion x')] = pmDistanceConversionX

        elif 'PM trap distance conversion y' in line:
            pmDistanceConversionY = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('PM trap distance conversion y')] = pmDistanceConversionY

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

            meta[standardized_name_of('AOD bead diameter')] = round(aodBeadDiameter, 2)
            meta[standardized_name_of('AOD bead radius')] = round(aodBeadRadius, 2)

        elif 'PM bead radius' in line:
            try:
                pmBeadRadius = float(line.strip().split(": ")[-1])
                if pmBeadRadius < 20:
                    pmBeadRadius = pmBeadRadius * 1000
                elif '(um)' in line:
                    pmBeadRadius = pmBeadRadius * 1000
            except:
                pmBeadRadius = 0

            pmBeadDiameter = 2.0 * pmBeadRadius

            meta[standardized_name_of('PM bead diameter')] = round(pmBeadDiameter, 2)
            meta[standardized_name_of('PM bead radius')] = round(pmBeadRadius, 2)

        elif 'Sample rate' in line:
            try:
                samplingRate = float(line.strip().split(": ")[-1])
                meta[standardized_name_of('Sample rate')] = samplingRate
            except:
                samplingRate = 1000
                meta[standardized_name_of('Sample rate')] = samplingRate

        elif 'Number of samples' in line:
            try:
                nSamples = int(line.strip().split(": ")[-1])
                meta[standardized_name_of('Number of samples')] = nSamples
            except:
                nSamples = 1
                meta[standardized_name_of('Number of samples')] = nSamples


        elif 'Laser Diode Operating Hours' in line:
            try:
                laserDiodeHours = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeHours = 0

            meta[standardized_name_of('Laser Diode Operating Hours')] = laserDiodeHours
            units['laserDiodeHours'] = 'h'

        elif 'Laser Diode Current' in line:
            try:
                laserDiodeCurrent = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeCurrent = 0

            meta[standardized_name_of('Laser Diode Current')] = laserDiodeCurrent
            units['laserDiodeCurrent'] = 'A'

        elif 'Laser Diode Temp' in line:
            try:
                laserDiodeTemp = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeTemp = 0

            meta[standardized_name_of('Laser Diode Temp')] = laserDiodeTemp
            units['laserDiodeTemp'] = 'C'

        elif 'number of blocks' in line or 'nBlocks' in line:
            try:
                nBlocks = int(line.strip().split(": ")[-1])
            except:
                nBlocks = 128

            meta[standardized_name_of('number of blocks')] = nBlocks
            units['nBlocks'] = None

        elif 'AOD vertical corner frequency' in line or 'yCornerFreqT2' in line:
            try:
                m = re.search(r'\s(\d+\.\d+)$', line.strip().strip('#').strip())
                value = float(m.group(1))
                meta[standardized_name_of('yCornerFreqT2')] = value
                units[standardized_name_of('yCornerFreqT2')] = standardized_unit_of('yCornerFreqT2')
            except:
                meta[standardized_name_of('yCornerFreqT2')] = None
                units[standardized_name_of('yCornerFreqT2')] = standardized_unit_of('yCornerFreqT2')

        elif 'PM vertical corner frequency' in line or 'yCornerFreqT1' in line:
            try:
                m = re.search(r'\s(\d+\.\d+)$', line.strip().strip('#').strip())
                value = float(m.group(1))
                meta[standardized_name_of('yCornerFreqT1')] = value
                units[standardized_name_of('yCornerFreqT1')] = standardized_unit_of('yCornerFreqT1')
            except:
                meta[standardized_name_of('yCornerFreqT1')] = None
                units[standardized_name_of('yCornerFreqT1')] = standardized_unit_of('yCornerFreqT1')

        elif 'xCornerFreqT1' in line or 'PM horizontal corner frequency' in line:
            value = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('xCornerFreqT1')] = value
            units[standardized_name_of('xCornerFreqT1')] = standardized_unit_of('xCornerFreqT1')

        elif 'xCornerFreqT2' in line or 'AOD horizontal corner frequency' in line:
            value = float(line.strip().split(": ")[-1])
            meta[standardized_name_of('xCornerFreqT2')] = value
            units[standardized_name_of('xCornerFreqT2')] = standardized_unit_of('xCornerFreqT2')

        else:
            if ":" in line:
                parts = line.split(": ")
            elif re.search('\w\s(\d|-\d)', line):
                parts = line.split(" ")

            try:
                if "." in parts[0]:
                    var, unit, value = parts[0].split(".")[0], parts[0].split(".")[1], float(parts[1])
                else:
                    var, unit, value = parts[0], None, float(parts[1])
            except:
                print()

            units[var] = unit
            meta[var] = value

    # parsing the date
    if dateString and time_string:
        combined_date = " ".join([dateString.strip(), time_string.strip()])
        try:
            date = pd.to_datetime(combined_date)
        except ValueError:
            combined_date = " ".join(["1/1/1900", time_string.strip()])
            date = pd.to_datetime(combined_date)
    elif dateString and not time_string:
        try:
            date = pd.to_datetime(dateString)
        except ValueError:
            date = pd.to_datetime(datetime(1900, 1, 1, 1, 1, 1))
    else:
        date = pd.to_datetime(datetime.now())

    meta['date'] = date

    CommentInfo = namedtuple('CommentInfo', ['metadata', 'units'])
    C = CommentInfo(meta, units)

    return C


def standardized_name_of(variable):
    """
    Maps various variable names onto a common pattern.

    :param str variable: str input variable

    """
    variable_mapper = {
        # general stuff
        'data averaged to while-loop': 'isDataAveraged',

        'number of samples': 'nSamples',
        'Number of samples': 'nSamples',
        'nSamples': 'nSamples',

        'sample rate': 'samplingRate',
        'Sample rate (Hz)': 'samplingRate',
        'Sample rate ': 'samplingRate',
        'Sample rate': 'samplingRate',
        'sampleRate.Hz': 'samplingRate',

        'rate of while-loop': 'recordingRate',
        'duration of measurement': 'measurementDuration',
        'dt ': 'timeStep',
        'dt': 'timeStep',

        'timeStep': 'timeStep',

        'Delta time ': 'deltaTime',
        'Delta time': 'deltaTime',

        'number of blocks': 'nBlocks',
        'nBlocks': 'nBlocks',

        'Viscosity': 'viscosity',
        'viscosity': 'viscosity',

        'Laser Diode Temp': 'laserDiodeTemp',
        'Laser Diode Operating Hours': 'laserDiodeHours',
        'Laser Diode Current': 'laserDiodeCurrent',

        # pm variables
        'PM horizontal corner frequency': 'pmCornerFreqX',
        'PM vertical corner frequency': 'pmCornerFreqY',

        'xCornerFreqT1.Hz': 'pmCornerFreqX',
        'xCornerFreqT1': 'pmCornerFreqX',
        'yCornerFreqT1.Hz': 'pmCornerFreqY',
        'yCornerFreqT1': 'pmCornerFreqY',

        'PM detector horizontal offset': 'pmDetectorOffsetX',
        'PM detector vertical offset': 'pmDetectorOffsetY',

        'xOffsetT1.V': 'pmDetectorOffsetX',
        'xOffsetT1': 'pmDetectorOffsetX',
        'yOffsetT1.V': 'pmDetectorOffsetY',
        'yOffsetT1': 'pmDetectorOffsetY',

        'PM horizontal trap stiffness': 'pmStiffnessX',
        'PM vertical trap stiffness': 'pmStiffnessY',

        'xStiffnessT1.pNperNm': 'pmStiffnessX',
        'yStiffnessT1.pNperNm': 'pmStiffnessY',

        'PM horizontal OLS': 'pmDisplacementSensitivityX',
        # 'PM horizontal OLS': 'pmDistanceConversionX',
        'PM vertical OLS': 'pmDisplacementSensitivityY',
        # 'PM vertical OLS': 'pmDistanceConversionY',

        'xDistConversionT1.VperNm': 'pmDisplacementSensitivityX',
        'yDistConversionT1.VperNm': 'pmDisplacementSensitivityY',

        # pm tweebot names
        'PM detector x offset': 'pmDetectorOffsetX',
        'PM detector y offset': 'pmDetectorOffsetY',
        'zOffsetT1.V': 'pmDetectorOffsetZ',

        'PM trap stiffness x': 'pmStiffnessX',
        'PM trap stiffness y': 'pmStiffnessY',

        'PM trap distance conversion x': 'pmDisplacementSensitivityX',
        'PM trap distance conversion y': 'pmDisplacementSensitivityY',

        # pm tweebot camera variables
        'PM ANDOR center x': 'andorPmCenterX',
        'PM ANDOR center y': 'andorPmCenterY',
        'PM ANDOR range x': 'andorPmRangeX',
        'PM ANDOR range y': 'andorPmRangeY',

        'PM CCD center x': 'ccdPmCenterX',
        'PM CCD center y': 'ccdPmCenterY',
        'PM CCD range x': 'ccdPmRangeX',
        'PM CCD range y': 'ccdPmRangeY',

        'PM bead diameter': 'pmBeadDiameter',
        'diameterT1.um': 'pmBeadDiameter',
        'PM bead radius': 'pmBeadRadius',

        # aod variables
        'AOD horizontal corner frequency': 'aodCornerFreqX',
        'AOD vertical corner frequency': 'aodCornerFreqY',

        'AOD detector horizontal offset': 'aodDetectorOffsetX',
        'AOD detector vertical offset': 'aodDetectorOffsetY',

        'AOD horizontal trap stiffness': 'aodStiffnessX',
        'AOD vertical trap stiffness': 'aodStiffnessY',

        'AOD horizontal OLS': 'aodDisplacementSensitivityX',
        # 'AOD horizontal OLS': 'aodDistanceConversionX',
        'AOD vertical OLS': 'aodDisplacementSensitivityY',
        # 'AOD vertical OLS': 'aodDistanceConversionY',

        # tweebot variables
        'AOD detector x offset': 'aodDetectorOffsetX',
        'AOD detector y offset': 'aodDetectorOffsetY',

        'AOD trap stiffness x': 'aodStiffnessX',
        'AOD trap stiffness y': 'aodStiffnessY',

        'xStiffnessT2.pNperNm': 'aodStiffnessX',
        'yStiffnessT2.pNperNm': 'aodStiffnessY',

        'AOD trap distance conversion x': 'aodDisplacementSensitivityX',
        'AOD trap distance conversion y': 'aodDisplacementSensitivityY',

        'xDistConversionT2.VperNm': 'aodDisplacementSensitivityX',
        'yDistConversionT2.VperNm': 'aodDisplacementSensitivityY',

        'AOD horizontal corner frequency': 'aodCornerFreqX',
        'AOD vertical corner frequency': 'aodCornerFreqY',

        'xCornerFreqT2.Hz': 'aodCornerFreqX',
        'xCornerFreqT2': 'aodCornerFreqX',
        'yCornerFreqT2.Hz': 'aodCornerFreqY',
        'yCornerFreqT2': 'aodCornerFreqY',

        'AOD detector horizontal offset': 'aodDetectorOffsetX',
        'AOD detector vertical offset': 'aodDetectorOffsetY',

        'AOD horizontal trap stiffness': 'aodStiffnessX',
        'AOD vertical trap stiffness': 'aodStiffnessY',

        'AOD horizontal OLS': 'aodDisplacementSensitivityX',
        # 'AOD horizontal OLS': 'aodDistanceConversionX',
        'AOD vertical OLS': 'aodDisplacementSensitivityY',
        # 'AOD vertical OLS': 'aodDistanceConversionY',

        # tweebot variables
        'xOffsetT2.V': 'aodDetectorOffsetX',
        'yOffsetT2.V': 'aodDetectorOffsetY',
        'zOffsetT2.V': 'aodDetectorOffsetZ',

        'AOD trap stiffness x': 'aodStiffnessX',
        'AOD trap stiffness y': 'aodStiffnessY',

        # 'AOD trap distance conversion x': 'aodDistanceConversionX',
        # 'AOD trap distance conversion y': 'aodDistanceConversionY',

        # aod tweebot camera variables
        'AOD ANDOR center x': 'andorAodCenterX',
        'AOD ANDOR center y': 'andorAodCenterY',
        'AOD ANDOR range x': 'andorAodRangeX',
        'AOD ANDOR range y': 'andorAodRangeY',

        'AOD CCD center x': 'ccdAodCenterX',
        'AOD CCD center y': 'ccdAodCenterY',
        'AOD CCD range x': 'ccdAodRangeX',
        'AOD CCD range y': 'ccdAodRangeY',

        'AOD bead diameter': 'aodBeadDiameter',
        'diameterT2.um': 'aodBeadDiameter',
        'AOD bead radius': 'aodBeadRadius',

        # andor camera specifics
        'ANDOR pixel size x': 'andorPixelSizeX',
        'ANDOR pixel size y': 'andorPixelSizeY',

        # ccd camera specifics
        'CCD pixel size x': 'ccdPixelSizeX',
        'CCD pixel size y': 'ccdPixelSizeY'

    }

    return variable_mapper.get(variable, None)


def standardized_unit_of(variable):
    """
    Maps various variable names onto their unit.

    :param str variable: str input variable

    """
    variable_mapper = {
        # general stuff
        'data averaged to while-loop': None,

        'number of samples': None,
        'nSamples': None,

        'sample rate': 'Hz',
        'sampleRate.Hz': 'Hz',

        'rate of while-loop': 'Hz',
        'duration of measurement': 's',
        'dt ': 's',

        'nBlocks': 'int',

        'Viscosity': 'pN s / nm^2',
        'viscosity': 'pN s / nm^2',

        'Laser Diode Temp': 'C',
        'Laser Diode Operating Hours': 'h',
        'Laser Diode Current': 'A',

        # pm variables
        'PM horizontal corner frequency': 'Hz',
        'PM vertical corner frequency': 'Hz',

        'xCornerFreqT1.Hz': 'Hz',
        'xCornerFreqT1': 'Hz',
        'yCornerFreqT1.Hz': 'Hz',
        'yCornerFreqT1': 'Hz',

        'PM detector horizontal offset': 'V',
        'PM detector vertical offset': 'V',

        'xOffsetT1.V': 'V',
        'yOffsetT1.V': 'V',

        'PM horizontal trap stiffness': 'pN/nm',
        'PM vertical trap stiffness': 'pN/nm',

        'xStiffnessT1.pNperNm': 'pN/nm',
        'yStiffnessT1.pNperNm': 'pN/nm',

        'PM horizontal OLS': 'V/nm',
        'PM vertical OLS': 'V/nm',

        'xDistConversionT1.VperNm': 'V/nm',
        'yDistConversionT1.VperNm': 'V/nm',

        # pm tweebot names
        'PM detector x offset': 'V',
        'PM detector y offset': 'V',
        'zOffsetT1.V': 'V',

        'PM trap stiffness x': 'pN/nm',
        'PM trap stiffness y': 'pN/nm',

        'PM trap distance conversion x': 'V/nm',
        'PM trap distance conversion y': 'V/nm',

        # pm tweebot camera variables
        'PM ANDOR center x': 'px',
        'PM ANDOR center y': 'px',
        'PM ANDOR range x': 'px',
        'PM ANDOR range y': 'px',

        'PM CCD center x': 'px',
        'PM CCD center y': 'px',
        'PM CCD range x': 'px',
        'PM CCD range y': 'px',

        'PM bead diameter': 'nm',
        'diameterT1.um': 'nm',

        # aod variables
        'AOD horizontal corner frequency': 'Hz',
        'AOD vertical corner frequency': 'Hz',

        'AOD detector horizontal offset': 'V',
        'AOD detector vertical offset': 'V',

        'AOD horizontal trap stiffness': 'pN/nm',
        'AOD vertical trap stiffness': 'pN/nm',

        'AOD horizontal OLS': 'V/nm',
        'AOD vertical OLS': 'V/nm',

        # tweebot variables
        'AOD detector x offset': 'V',
        'AOD detector y offset': 'V',

        'AOD trap stiffness x': 'pN/nm',
        'AOD trap stiffness y': 'pN/nm',

        'xStiffnessT2.pNperNm': 'pN/nm',
        'yStiffnessT2.pNperNm': 'pN/nm',

        'AOD trap distance conversion x': 'V/nm',
        'AOD trap distance conversion y': 'V/nm',

        'xDistConversionT2.VperNm': 'V/nm',
        'yDistConversionT2.VperNm': 'V/nm',

        'AOD horizontal corner frequency': 'Hz',
        'AOD vertical corner frequency': 'Hz',

        'xCornerFreqT2.Hz': 'Hz',
        'xCornerFreqT2': 'Hz',
        'yCornerFreqT2.Hz': 'Hz',
        'yCornerFreqT2': 'Hz',

        'AOD detector horizontal offset': 'V',
        'AOD detector vertical offset': 'V',

        'AOD horizontal trap stiffness': 'pN/nm',
        'AOD vertical trap stiffness': 'pN/nm',

        'AOD horizontal OLS': 'V/nm',
        'AOD vertical OLS': 'V/nm',

        # tweebot variables
        'xOffsetT2.V': 'V',
        'yOffsetT2.V': 'V',
        'zOffsetT2.V': 'V',

        'AOD trap stiffness x': 'pN/nm',
        'AOD trap stiffness y': 'pN/nm',

        'AOD trap distance conversion x': 'V/nm',
        'AOD trap distance conversion y': 'V/nm',

        # aod tweebot camera variables
        'AOD ANDOR center x': 'px',
        'AOD ANDOR center y': 'px',
        'AOD ANDOR range x': 'px',
        'AOD ANDOR range y': 'px',

        'AOD CCD center x': 'px',
        'AOD CCD center y': 'px',
        'AOD CCD range x': 'px',
        'AOD CCD range y': 'px',

        'AOD bead diameter': 'nm',
        'diameterT2.um': 'nm',

        # andor camera specifics
        'ANDOR pixel size x': 'nm/px',
        'ANDOR pixel size y': 'nm/px',

        # ccd camera specifics
        'CCD pixel size x': 'nm/px',
        'CCD pixel size y': 'nm/px'

    }

    return variable_mapper.get(variable, None)
