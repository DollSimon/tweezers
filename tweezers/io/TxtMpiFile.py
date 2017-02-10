from pathlib import Path
from collections import OrderedDict
import re
import json
import pandas as pd
import numpy as np

from tweezers import MetaDict, UnitDict
import tweezers.ixo.utils as ixo


class TxtMpiFile():
    """
    A helper object to extract data from MPI-styled txt-files. Especially to get all header lines and all data lines.
    Note that this reads the files with `UTF-8` encoding.
    """

    def __init__(self, path):
        """
        Args:
            path (:class:`patlhlib.Path`): path to file to read, if the input is of a different type, it is given to
                                           :class:`pathlibh.Path` to try to create an instance
        """

        # adjust input to the correct format
        if not isinstance(path, Path):
            self.path = Path(path)
        else:
            self.path = path

        # check for empty file
        if self.path.stat().st_size == 0:
            raise ValueError('Empty file given: ' + str(self.path))

        # JSON header present?
        with self.path.open(encoding='utf-8') as f:
            firstLine = f.readline().strip()
        if firstLine.startswith('{'):
            self.isJson = True
        else:
            self.isJson = False

    def getMetadata(self):
        """
        Read the metadata from the file. Returns output of :meth:`.readMeta`.
        """
        if self.isJson:
            return self.readMetaJson()
        else:
            return self.readMeta()

    def getData(self):
        """
        Reads the data from the file. Returns output of :meth:`.readData`.
        """

        if self.isJson:
            return self.readDataJson()
        else:
            return self.readData()

    def getDataSegment(self, nstart, nrows):
        """
        Reads a segment of data from the file.

        Args:
            nstart: data-row to start reading in the file
            nrows: number of rows to read

        Returns:
            :class:`pandas.DataFrame`
        """

        if self.isJson:
            cols = self.readColumnTitlesJson()
        else:
            cols = self.readColumnTitles()

        data = pd.read_csv(self.path, sep='\t', dtype=np.float64, skiprows=cols['n'] + nstart,
                           nrows=nrows, header=None, names=cols['names'], comment='#', engine='c')

        return data

    def readMetaJson(self):
        """
        Read the metadata from a JSON formatted data file.

        Returns:
            - :class:`.MetaDict` -- metadata
            - :class:`.UnitDict` -- units
        """

        headerStr = ''
        with self.path.open(encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    break
                else:
                    headerStr += line

        header = json.loads(headerStr, object_pairs_hook=OrderedDict)
        units = UnitDict(header.pop('units'))
        meta = MetaDict(header)

        return meta, units

    def readMeta(self):
        """
        Read the metadata from a normally (raw) formatted data file.

        Returns:
            - :class:`.MetaDict` -- metadata
            - :class:`.UnitDict` -- units
        """

        headerLines = []
        with self.path.open(encoding='utf-8') as f:
            for line in f:
                if line.strip() and line.startswith('#'):
                    headerLines.append(line)
        meta, units = self.convertHeader(headerLines)

        # read units from columns
        cols = self.readColumnTitles()
        units.update(cols['units'])

        return meta, units

    def readDataJson(self):
        """
        Read the data from a JSON formatted data file.

        Returns:
            :class:`pandas.DataFrame`
        """

        cols = self.readColumnTitlesJson()
        data = pd.read_csv(self.path, sep='\t', dtype=np.float64, skiprows=cols['n'], header=None,
                           names=cols['names'], engine='c')
        return data

    def readData(self):
        """
        Read the data from a normally (raw) formatted data file.

        Returns:
            :class:`pandas.DataFrame`
        """

        cols = self.readColumnTitles()

        data = pd.read_csv(self.path, sep='\t', dtype=np.float64, skiprows=cols['n'],
                           header=None, names=cols['names'], comment='#', engine='c')
        return data

    def convertHeader(self, headerLines):
        """
        Convert the meta data given as a list of header lines to a meta data structure.

        Args:
            headerLines (`list` of :class:`str`): list of header lines

        Returns:
            - :class:`.MetaDict` -- metadata
            - :class:`.UnitDict` -- units
        """

        meta = MetaDict()
        units = UnitDict()
        # regular expression explained:
        # - optionally start with '# '
        # - string that can contain everything except ':' and '(' -> meta identifier
        # - optional whitespace followed by a unit: string with anything but ':', lazy, within brackets '()'
        # - whitespace or ':'
        # - value can be either:
        #   - optional whitespace followed by any character
        #   - anything without whitespaces (required for lines without ':' as separator)
        # - optional final unit consisting of any letter except 'PM' (exclude time stuff)
        regex = re.compile('^(# )?(?P<name>[^(:\d]*)\s?(\((?P<unit>[^:]*?)\)\s?)?(:|\s)(?P<value>\s?.+?|[^\s]+)(?! PM)(?P<unit2>\s\D+)?$')
        for line in headerLines:
            # check if line should be ignored
            if self.isIgnoredHeader(line):
                continue
            # perform regular expression search
            res = regex.search(line)

            # no match or empty name or value? go to next line
            if not res or res.group('name') is None or res.group('value') is None:
                continue

            # get list of keys to the object, usually not longer than 2
            key = self.getStandardIdentifier(res.group('name'))
            # check for value type in MetaDict
            value = res.group('value').strip()
            valueKey = key[-1]
            value = self.getValueType(valueKey, value)

            # get date and time properly, different for all files
            if key[0] == 'date':
                # do we also have the time appended?
                splitted = value.split('\t')
                try:
                    meta['time'] = splitted[1]
                except IndexError:
                    pass
                value = splitted[0].replace('/', '.')

            # store value
            self.setMeta(meta, key, value)
            unit = None
            if not res.group('unit') is None:
                unit = res.group('unit').strip()
            elif not res.group('unit2') is None:
                unit = units, key, res.group('unit2').strip()
            if unit:
                self.setMeta(units, key, unit)

        return meta, units

    def readColumnTitles(self):
        """
        Read the column names, their units and the number of header lines from a normally formatted file.

        Returns:
            `dict` with keys `names` (`list`), `units` (:class:`.UnitDict`) and `n`
        """

        # get column line
        n = 0
        with self.path.open(encoding='utf-8') as f:
            for line in f:
                n += 1
                if line and line.startswith('P'):
                    columnLine = line
                    break

        # get column units
        regex = re.compile('(\w+(?:\s\w+)*)(?:\s*\(([^)]*)\))?')
        res = regex.findall(columnLine)

        columns = []
        units = UnitDict()
        for (column, unit) in res:
            # delete whitespaces for consistency
            column = column.replace(' ', '')
            # get standard name
            column = self.getStandardIdentifier(column)[0]
            columns.append(column)
            if unit:
                units[column] = unit

        return {'names': columns, 'units': units, 'n': n}

    def readColumnTitlesJson(self):
        """
        Read the column names, their units and the number of header lines from a JSON formatted file.

        Returns:
            `dict` with keys `names` (`list`), `units` (:class:`.UnitDict`) and `n`
        """

        # read header line
        n = 0
        with self.path.open(encoding='utf-8') as f:
            for line in f:
                n += 1
                if line.startswith('#'):
                    # skip empty line
                    next(f)
                    columnLine = next(f)
                    n += 2
                    break

        # get column title names with units
        regex = re.compile('(\w+)(?:\s\[(\w*)\])?')
        header = regex.findall(columnLine)

        # store them in a UnitDict
        colHeaders = []
        colUnits = UnitDict()
        for (colHeader, unit) in header:
            colHeaders.append(colHeader)
            if unit:
                colUnits[colHeader] = unit

        return {'names': colHeaders, 'units': colUnits, 'n': n}

    def setMeta(self, meta, keyList, value):
        """
        Set an item in a dictionary (e.g. :class:`tweezers.MetaDict`) based on a list of keys that describe the path
        to the value.

        Args:
            meta (dict): dictionary to update, in this context it will be :class:`tweezers.MetaDict` or
                         :class:`tweezers.UnitDict`
            keyList (list): list of keys
            value: the value to store
        """

        path = {keyList[-1]: value}

        # if there are keys left, we need to build a nested structure
        for key in reversed(keyList[:-1]):
            path = {key: path}

        meta.update(path)

    def getTrialNumber(self):
        """
        Extract the trial number from the file name.

        Returns:
            `str`
        """

        res = re.match('^([A-Z]+_)?(?P<trial>\d+)', self.path.stem)
        return res.group('trial')

    @staticmethod
    def getStandardIdentifier(key):
        """
        Translate a header key to a unique identifier. This is necessary as several versions of header keys are around.

        Args:
            key (`str`): the key to look up

        Returns:
            `list` of `str`
        """

        # reduce number of variations: strip spaces
        # one could also change everything to lower case but that would decrease readability
        key = key.strip()

        keyMapper = {
            # column titles
            'freq': 'f',
            'PMx': 'pmX',
            'PMy': 'pmY',
            'AODx': 'aodX',
            'AODy': 'aodY',
            'PSDPMx': 'pmX',
            'PSDPMy': 'pmY',
            'PSDAODx': 'aodX',
            'PSDAODy': 'aodY',
            'FitPMx': 'pmXFit',
            'FitPMy': 'pmYFit',
            'FitAODx': 'aodXFit',
            'FitAODy': 'aodYFit',
            'PMxdiff': 'pmXDiff',
            'PMydiff': 'pmYDiff',
            'PMxsum': 'pmXSum',
            'AODxdiff': 'aodXDiff',
            'AODydiff': 'aodYDiff',
            'AODxsum': 'aodXSum',
            'FBxsum': 'fbXSum',
            'FBx': 'fbX',
            'FBy': 'fbY',
            'xdist': 'xDist',
            'ydist': 'yDist',
            'PMsensorx': 'pmXSensor',
            'PMsensory': 'pmYSensor',
            'TrackingReferenceTime': 'trackingReferenceTime',

            # general stuff
            'Date of Experiment': 'date',
            'Time of Experiment': 'time',
            'measurement starttime': 'time',
            'data averaged to while-loop': 'isDataAveraged',

            'number of samples': 'nSamples',
            'Number of samples': 'nSamples',

            'sample rate': 'samplingRate',
            'Sample rate (Hz)': 'samplingRate',
            'Sample rate': 'samplingRate',
            'sampleRate.Hz': 'samplingRate',

            'rate of while-loop': 'recordingRate',
            'duration of measurement': 'measurementDuration',
            'dt': 'dt',
            'Delta time': 'dt',

            'number of blocks': 'psdNBlocks',

            'Viscosity': 'viscosity',

            'Laser Diode Temp': 'laserDiodeTemp',
            'Laser Diode Operating Hours': 'laserDiodeHours',
            'Laser Diode Current': 'laserDiodeCurrent',

            'errors': 'errors',
            'start of measurement': 'startOfMeasurement',
            'end of measurement': 'endOfMeasurement',

            # aod variables
            'AOD horizontal corner frequency': ['aodX', 'cornerFrequency'],
            'AOD vertical corner frequency': ['aodY', 'cornerFrequency'],
            'AOD detector horizontal offset': ['aodX', 'zeroOffset'],
            'AOD detector vertical offset': ['aodY', 'zeroOffset'],
            'AOD horizontal trap stiffness': ['aodX', 'stiffness'],
            'AOD vertical trap stiffness': ['aodY', 'stiffness'],
            'AOD horizontal OLS': ['aodX', 'displacementSensitivity'],
            'AOD vertical OLS': ['aodY', 'displacementSensitivity'],

            # pm variables
            'PM horizontal corner frequency': ['pmX', 'cornerFrequency'],
            'PM vertical corner frequency': ['pmY', 'cornerFrequency'],
            'PM detector horizontal offset': ['pmX', 'zeroOffset'],
            'PM detector vertical offset': ['pmY', 'zeroOffset'],
            'PM horizontal trap stiffness': ['pmX', 'stiffness'],
            'PM vertical trap stiffness': ['pmY', 'stiffness'],
            'PM horizontal OLS': ['pmX', 'displacementSensitivity'],
            'PM vertical OLS': ['pmY', 'displacementSensitivity'],

            # aod tweebot variables
            'AOD detector x offset': ['aodX', 'zeroOffset'],
            'AOD detector y offset': ['aodY', 'zeroOffset'],
            'AOD trap stiffness x': ['aodX', 'stiffness'],
            'AOD trap stiffness y': ['aodY', 'stiffness'],

            'xStiffnessT2.pNperNm': ['aodX', 'stiffness'],
            'yStiffnessT2.pNperNm': ['aodY', 'stiffness'],

            'AOD trap distance conversion x': ['aodX', 'displacementSensitivity'],
            'AOD trap distance conversion y': ['aodY', 'displacementSensitivity'],

            'xDistConversionT2.VperNm': ['aodX', 'displacementSensitivity'],
            'yDistConversionT2.VperNm': ['aodY', 'displacementSensitivity'],

            'xCornerFreqT2.Hz': ['aodX', 'cornerFrequency'],
            'xCornerFreqT2': ['aodX', 'cornerFrequency'],
            'yCornerFreqT2.Hz': ['aodY', 'cornerFrequency'],
            'yCornerFreqT2': ['aodY', 'cornerFrequency'],

            'xOffsetT2.V': ['aodX', 'zeroOffset'],
            'yOffsetT2.V': ['aodY', 'zeroOffset'],
            'zOffsetT2.V': ['aodZ', 'zeroOffset'],

            # pm tweebot variables
            'PM detector x offset': ['pmX', 'zeroOffset'],
            'PM detector y offset': ['pmY', 'zeroOffset'],

            'PM trap stiffness x': ['pmX', 'stiffness'],
            'PM trap stiffness y': ['pmY', 'stiffness'],

            'xStiffnessT1.pNperNm': ['pmX', 'stiffness'],
            'yStiffnessT1.pNperNm': ['pmY', 'stiffness'],

            'PM trap distance conversion x': ['pmX', 'displacementSensitivity'],
            'PM trap distance conversion y': ['pmY', 'displacementSensitivity'],

            'xDistConversionT1.VperNm': ['pmX', 'displacementSensitivity'],
            'yDistConversionT1.VperNm': ['pmY', 'displacementSensitivity'],

            'xCornerFreqT1.Hz': ['pmX', 'cornerFrequency'],
            'xCornerFreqT1': ['pmX', 'cornerFrequency'],
            'yCornerFreqT1.Hz': ['pmY', 'cornerFrequency'],
            'yCornerFreqT1': ['pmY', 'cornerFrequency'],

            'xOffsetT1.V': ['pmX', 'zeroOffset'],
            'xOffsetT1': ['pmX', 'zeroOffset'],
            'yOffsetT1.V': ['pmY', 'zeroOffset'],
            'yOffsetT1': ['pmY', 'zeroOffset'],
            'zOffsetT1.V': ['pmZ', 'zeroOffset'],

            # aod tweebot camera variables
            'AOD ANDOR center x': ['aodX', 'andorCenter'],
            'AOD ANDOR center y': ['aodY', 'andorCenter'],
            'AOD ANDOR range x': ['aodX', 'andorRange'],
            'AOD ANDOR range y': ['aodY', 'andorRange'],

            'AOD CCD center x': ['aodX', 'ccdCenter'],
            'AOD CCD center y': ['aodY', 'ccdCenter'],
            'AOD CCD range x': ['aodX', 'ccdRange'],
            'AOD CCD range y': ['aodY', 'ccdRange'],

            # pm tweebot camera variables
            'PM ANDOR center x': ['pmX', 'andorCenter'],
            'PM ANDOR center y': ['pmY', 'andorCenter'],
            'PM ANDOR range x': ['pmX', 'andorRange'],
            'PM ANDOR range y': ['pmY', 'andorRange'],

            'PM CCD center x': ['pmX', 'ccdCenter'],
            'PM CCD center y': ['pmY', 'ccdCenter'],
            'PM CCD range x': ['pmX', 'ccdRange'],
            'PM CCD range y': ['pmY', 'ccdRange'],

            # bead
            'PM bead diameter': ['pmX', 'beadDiameter'],
            'diameterT1.um': ['pmX', 'beadDiameter'],
            'PM bead radius': ['pmX', 'beadRadius'],

            'AOD bead diameter': ['aodX', 'beadDiameter'],
            'diameterT2.um': ['aodX', 'beadDiameter'],
            'AOD bead radius': ['aodX', 'beadRadius'],

            # andor camera specifics
            'ANDOR pixel size x': 'andorXPixelSize',
            'ANDOR pixel size y': 'andorYPixelSize',

            # ccd camera specifics
            'CCD pixel size x': 'ccdXPixelSize',
            'CCD pixel size y': 'ccdYPixelSize'
        }

        res = key
        if key in keyMapper.keys():
            res = keyMapper[key]
        # make sure we return a list
        if isinstance(res, str):
            return [res]
        else:
            return res

    @staticmethod
    def getValueType(key, value):
        """
        Convert the value of a header key from string to the correct format. If no format is given, the input value is
        returned.

        Args:
            key (`str`): header key to look up
            value (`str`): value to convert

        Returns:
            converted value
        """

        keyMapper = {

            # general stuff
            'title': str,
            'time': str,

            # axis variables
            'forceSensitivity': float,

            # general stuff
            'date': lambda x: x.replace('\t', ' '),
            'isDataAveraged': ixo.strToBool,
            'nSamples': lambda x: int(float(x)),
            'psdNSamples': int,
            'psdSamplingRate': int,
            'tsNSamples': int,
            'tsTimeStep': float,
            'samplingRate': int,
            'recordingRate': int,
            'measurementDuration': float,
            'timeStep': float,
            'dt': float,
            'psdBlockLength': int,
            'psdOverlap': int,
            'psdNBlocks': lambda x: int(float(x)),
            'viscosity': float,

            'laserDiodeTemp': float,
            'laserDiodeHours': float,
            'laserDiodeCurrent': float,

            'errors': lambda x: [int(error) for error in x.split('\t')],

            'startOfMeasurement': int,
            'endOfMeasurement': int,

            # axis variables
            'cornerFrequency': float,
            'zeroOffset': float,
            'stiffness': float,
            'displacementSensitivity': lambda x: 1 / float(x),

            # bead
            'beadDiameter': float,
            'beadRadius': float,

            # tweebot camera variables
            'andorCenter': float,
            'andorRange': float,
            'ccdCenter': float,
            'ccdRange': float,

            # andor camera specifics
            'andorXPixelSize': float,
            'andorYPixelSize': float,

            # ccd camera specifics
            'ccdXPixelSize': float,
            'ccdYPixelSize': float,
        }

        if key in keyMapper:
            return keyMapper[key](value)
        else:
            return value

    @staticmethod
    def isIgnoredHeader(line):
        """
        Check if a header line should be ignored.

        Args:
            line (`str`): header line to check

        Returns:
            :class:`bool`
        """

        ignoredLines = [
            '# Laser Diode Status',
            '# results thermal calibration:',
        ]

        if line in ignoredLines:
            return True
        elif line.startswith('### File created by selecting data between'):
            return True
        else:
            return False
