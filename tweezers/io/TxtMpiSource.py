from pathlib import Path
import json
import re
import pandas as pd
from io import StringIO
import numpy as np
from collections import OrderedDict
import os

from .TxtFileMpi import TxtFileMpi
from .BaseSource import BaseSource
import tweezers as t
import tweezers.ixo.utils as ixo


class TxtMpiSource(BaseSource):
    """
    Data source for *.txt files from the MPI with the old style header or the new JSON format.
    """

    def __init__(self, data=None, psd=None, ts=None):
        """
        Constructor for TxtMpiSource

        Args:
            path (:class:`patlhlib.Path`): path to file to read, if the input is of a different type, it is given to
                                           :class:`pathlibh.Path` to try to create an instance
        """

        super().__init__()

        # go through input
        if data:
            self.data = TxtFileMpi(data)
        else:
            self.data = None

        if psd:
            self.psd = TxtFileMpi(psd)
        else:
            self.psd = None

        if ts:
            self.ts = TxtFileMpi(ts)
        else:
            self.ts = None

    def getMetadata(self):
        """
        Return the metadata of the experiment.

        Returns:
            :class:`tweezers.MetaDict` and :class:`tweezers.UnitDict`
        """

        # keep variables local so they are not stored in memory
        meta, units = self.getDefaultMeta()

        # check each available file for header information
        # sequence is important since later calls overwrite earlier ones so if a header is present in "psd" and
        # "data", the value from "data" will be returned
        if self.ts:
            # get header data from file
            metaLines, unitsTmp = self.ts.getHeader()
            # if we got units for the column names, update them
            if unitsTmp:
                units.update(unitsTmp)
            # convert header to corresponding dict format
            metaTmp, unitsTmp = self.convertHeader(metaLines)

            # make sure we don't override important stuff that by accident has the same name
            self.renameKey('nSamples', 'psdNSamples', meta=metaTmp, units=unitsTmp)
            self.renameKey('dt', 'psdDt', meta=metaTmp, units=unitsTmp)

            # set time series unit
            unitsTmp['timeseries'] = 'V'

            # update the dictionaries with newly found values
            meta.update(metaTmp)
            units.update(unitsTmp)

        if self.psd:
            metaTmp, unitsTmp = self.psd.getHeader()
            if unitsTmp:
                units.update(unitsTmp)
            metaTmp, unitsTmp = self.convertHeader(metaTmp)

            # make sure we don't override important stuff that by accident has the same name
            # also, 'nSamples' and 'samplingRate' in reality refer to the underlying timeseries data
            self.renameKey('nSamples', 'psdNSamples', meta=metaTmp, units=unitsTmp)
            self.renameKey('dt', 'psdDt', meta=metaTmp, units=unitsTmp)

            # set psd unit
            unitsTmp['psd'] = 'V^2 / Hz'

            meta.update(metaTmp)
            units.update(unitsTmp)

        if self.data:
            metaTmp, unitsTmp = self.data.getHeader()
            if unitsTmp:
                units.update(unitsTmp)
            metaTmp, unitsTmp = self.convertHeader(metaTmp)

            # rename variables for the sake of consistency and compatibility with Matlab and because the naming is
            # confusing: samplingRate is actually the acquisition rate since the DAQ card averages the data already
            # the sampling rate should describe the actual time step between data points not something else
            if 'recordingRate' in metaTmp:
                self.renameKey('samplingRate', 'acquisitionRate', meta=metaTmp, units=unitsTmp)
                self.renameKey('recordingRate', 'samplingRate', meta=metaTmp, units=unitsTmp)
                self.renameKey('nSamples', 'nAcquisitionsPerSample', meta=metaTmp)

            # add trial number
            metaTmp['trial'] = self.data.getTrialNumber()

            # update dictionaries
            meta.update(metaTmp)
            units.update(unitsTmp)

        # add title string to metadata, used for plots
        self.setTitle(meta)

        # make sure all axes have the beadRadius
        meta['pmY']['beadRadius'] = meta['pmX']['beadRadius']
        units['pmY']['beadRadius'] = units['pmX']['beadRadius']
        meta['aodY']['beadRadius'] = meta['aodX']['beadRadius']
        units['aodY']['beadRadius'] = units['aodX']['beadRadius']

        return meta, units

    def getData(self):
        """
        Return the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.data:
            raise ValueError('No data file given.')

        # read the data and column headers from file
        columnHeader, data = self.data.getData()
        # convert the column headers to a standardized format
        columnHeader = self.convertColumns(columnHeader)
        # convert the data to a standardized format
        data = self.convertData(columnHeader, data)
        return data

    def getPsd(self):
        """
        Return the PSD of the thermal calibration of the experiment as computed by LabView.

        Returns:
            :class:`pandas.DataFrame`
        """

        # read psd file which also contains the fitting
        data = self.readPsd()
        # ignore the fitting
        titles = [title for title, column in data.iteritems() if not title.endswith('Fit')]
        return data[titles]

    def getPsdFit(self):
        """
        Return the LabView fit of the Lorentzian to the PSD.

        Returns:
            :class:`pandas.DataFrame`
        """

        # the fit is in the psd file
        data = self.readPsd()
        # only choose frequency and fit columns
        titles = [title for title, column in data.iteritems() if title.endswith('Fit') or title == 'f']
        return data[titles]

    def getTs(self):
        """
        Return the time series recorded for thermal calibration.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.ts:
            raise ValueError('No time series file given.')

        columnHeader, data = self.ts.getData()
        columnHeader = self.convertColumns(columnHeader)
        # remove "Diff" from column headers
        columnHeader = [title.split('Diff')[0] for title in columnHeader]
        # convert data to pandas dataframe
        data = self.convertData(columnHeader, data)
        return data

    def readPsd(self):
        """
        Read the PSD file given by LabView which actually contains the PSD and the LabView fit to it.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.psd:
            raise ValueError('No PSD file given.')

        # read the psd
        columnHeader, data = self.psd.getData()
        # convert column titles to standardized format
        columnHeader = self.convertColumns(columnHeader)
        # convert data to correct format
        data = self.convertData(columnHeader, data)
        return data

    def setTitle(self, meta):
        """
        Set the 'title' key in the metadata dictionary based on date and trial number if they are available. This
        string is e.g. used for plots.

        Args:
            meta

        Returns:
            :class:`tweezers.MetaDict`
        """

        title = ''
        try:
            title += meta['date'] + ' '
        except KeyError:
            pass
        try:
            title += meta['time'] + ' '
        except KeyError:
            pass
        try:
            title += meta['trial']
        except KeyError:
            pass

        meta['title'] = title.strip()

    def convertHeader(self, header):
        """
        Convert the meta data given as a list of header lines to a meta data structure.

        Args:
            header (:class:`list` of :class:`str`): list of header lines
            columnUnits (:class:`dict`): unit values to add to the units dictionary in the end, this will overwrite
            existing values

        Returns:
            :class:`tweezers.MetaDict` and :class:`tweezers.UnitDict`
        """

        # JSON header?
        if header[0].startswith('{'):
            # create single string
            header = ''.join(header)
            # and then be converted
            meta = json.loads(header, object_pairs_hook=OrderedDict)
            units = t.UnitDict(meta.pop('units'))
            meta = t.MetaDict(meta)
        else:
            meta = t.MetaDict()
            units = t.UnitDict()
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
            for line in header:
                # check if line should be ignored
                if TxtMpiSource.isIgnoredHeader(line):
                    continue
                # perform regular expression search
                res = regex.search(line)

                # no match or empty name or value? go to next line
                if not res or res.group('name') is None or res.group('value') is None:
                    continue

                # get list of keys to the object, usually not longer than 2
                key = TxtMpiSource.getStandardIdentifier(res.group('name'))
                # check for value type in MetaDict
                value = res.group('value').strip()
                valueKey = key[-1]
                if valueKey in t.MetaDict.knownKeyTypes.keys():
                    value = t.MetaDict.knownKeyTypes[valueKey](value)
                else:
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

                # ensure bead radius, some have only diameter
                if key[-1] == 'beadDiameter':
                    key[-1] = 'beadRadius'
                    value /= 2
                    self.setMeta(meta, key, value)
                    if unit:
                        self.setMeta(units, key, unit)

        return meta, units

    def convertColumns(self, struct):
        """
        Convert column header to standardized format. Works with lists or dictionary by replacing the values (list)
        or the keys (dict). Does not work for nested lists or dictionaries.

        Args:
            columnHeader (:class:`list` of :class:`str` or :class:`dict`)

        Returns:
            :class:`list` of :class:`str` or :class:`dict`
        """

        if isinstance(struct, dict):
            # we have to get a list of keys first since we modify the dict in place and would get an infinite loop
            # else (at least in case of OrderedDict)
            keys = list(struct.keys())
            for key in keys:
                newKey = self.getStandardIdentifier(key)[0]
                struct[newKey] = struct.pop(key)
        else:
            for i in range(len(struct)):
                struct[i] = self.getStandardIdentifier(struct[i])[0]
        return struct

    def convertData(self, columnHeader, data):
        """
        Convert the data to a :class:`pandas.DataFrame` with the given columnHeaders.

        Args:
            columnHeader (list): list of :class:`str` with column headers
            data (str): string from the file that holds the data, tab-spaced values

        Returns:
            :class:`pandas.DataFrame`
        """

        # read data into pandas.DataFrame
        data = pd.read_csv(StringIO(data), sep='\t', names=columnHeader, dtype=np.float64)
        return data

    def save(self, container, path=None):
        """
        Writes the data of a :class:`tweezers.TweezersData` to disk. This preservers the `data` and`thermalCalibration`
        folder structure. `path` should be the folder that holds these subfolders. If it is empty, the original files
        will be overwritten.

        Args:
            container (:class:`tweezers.TweezersData`): data to write
            path (:class:`pathlib.Path`): path to a folder for the dataset, if not set, the original data will be
                                          overwritten
        """

        if not isinstance(path, Path):
            path = Path(path)

        data = ['ts', 'psd', 'data']

        # list of input files and their data from the container, these are the ones we're writing back
        # this is also important for the laziness of the TweezerData object
        files = [[getattr(self, file), getattr(container, file)] for file in data if getattr(self, file)]
        if not files:
            return

        # get root path if not given
        if not path:
            path = files[0][0].path.parents[1]

        meta = container.meta
        meta['units'] = container.units

        # now write all of it
        for file in files:
            filePath = path / file[0].path.parent.name / file[0].path.name
            self.writeData(meta, file[1], filePath)

    def writeData(self, meta, data, path):
        """
        Write experiment data back to a target file. Note that this writes the data in an `UTF-8` encoding.
        Implementing this is not required for a data source but used here to convert the header to JSON.

        Args:
            meta (:class:`tweezers.MetaDict`): meta data to store
            data (:class:`pandas.DataFrame`): data to write back
            path (:class:`pathlib.Path`): path where to write the file
        """

        # ensure directory exists
        try:
            os.makedirs(str(path.parent))
        except FileExistsError:
            pass

        # write the data
        with path.open(mode='w', encoding='utf-8') as f:
            f.write(json.dumps(meta,
                               indent=4,
                               ensure_ascii=False,
                               sort_keys=True))
            f.write("\n\n#### DATA ####\n\n")

        data.to_csv(path_or_buf=str(path), sep='\t', mode='a', index=False)

    def getDefaultMeta(self):
        """
        Set default values for metadata and units. This will be overwritten by values in the data files if they exist.

        Returns:
            :class:`tweezers.MetaDict` and :class:`tweezers.UnitDict`
        """

        meta = t.MetaDict()
        units = t.UnitDict()

        # meta[self.getStandardIdentifier('tsSamplingRate')] = 80000
        #
        # units[self.getStandardIdentifier('tsSamplingRate')] = 'Hz'

        return meta, units

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

    def renameKey(self, oldKey, newKey, meta=None, units=None):
        """
        Rename a key in the meta- and units-dictionaries. Does not work for nested dictionaries.

        Args:
            meta (:class:`tweezers.MetaDict`): meta dictionary
            units (:class:`tweezers.UnitDict`): units dictionary (can be an empty one if not required)
            oldKey (str): key to be renamed
            newKey (str): new key name
        """

        if meta:
            if oldKey not in meta:
                return
            meta.replaceKey(oldKey, newKey)
        if units:
            if oldKey not in units:
                return
            units.replaceKey(oldKey, newKey)

    @staticmethod
    def getValueType(key, value):
        """
        Convert the value of a header key from string to the correct format. If no format is given, the input value is
        returned.

        Args:
            key (string): header key to look up
            value (string): value to convert

        Returns:
            converted value
        """

        keyMapper = {
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
            'displacementSensitivity': float,

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
    def getStandardIdentifier(key):
        """
        Translate a header key to a unique identifier. This is necessary as several versions of header keys are around.

        Args:
            key (str): the key to look up

        Returns:
            list
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
    def isIgnoredHeader(line):
        """
        Check if a header line should be ignored.

        Args:
            line (str): header line to check

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
