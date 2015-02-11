from pathlib import Path
import json
import re
import pandas as pd
from io import StringIO
import numpy as np
from collections import OrderedDict
from .TxtFileMpi import TxtFileMpi
from .BaseSource import BaseSource

import tweezers as c
import ixo.utils as ixo


class TxtSourceMpi(BaseSource):
    """
    Data source for *.txt files from the MPI with the old style header or the new JSON format.
    """

    def __init__(self, data=None, psd=None, ts=None):
        """
        Constructor for TxtSourceMpi

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

    def get_metadata(self):
        """
        Return the metadata of the experiment.

        Returns:
            :class:`tweezers.MetaDict`
        """

        # keep variables local so they are not stored in memory
        meta, units = self.get_default_meta()

        # check each available file for header information
        # sequence is important since later calls overwrite earlier ones so if a header is present in "psd" and
        # "data", the value from "data" will be returned
        if self.ts:
            # get header data from file
            metaTmp, unitsTmp = self.ts.get_header()
            # convert header to corresponding dict format
            metaTmp, unitsTmp = self.convert_header(metaTmp, unitsTmp)

            # make sure we don't override important stuff that by accident has the same name
            self.rename_key(metaTmp, unitsTmp, 'nSamples', 'nSamplesTs')
            self.rename_key(metaTmp, unitsTmp, 'timeStep', 'timeStepTs')

            # update the dictionaries with newly found values
            meta.update(metaTmp)
            units.update(unitsTmp)

        if self.psd:
            metaTmp, unitsTmp = self.psd.get_header()
            metaTmp, unitsTmp = self.convert_header(metaTmp, unitsTmp)

            # make sure we don't override important stuff that by accident has the same name
            self.rename_key(metaTmp, unitsTmp, 'nSamples', 'nSamplesPsd')
            self.rename_key(metaTmp, unitsTmp, 'samplingRate', 'samplingRatePsd')

            meta.update(metaTmp)
            units.update(unitsTmp)

        if self.data:
            metaTmp, unitsTmp = self.data.get_header()
            metaTmp, unitsTmp = self.convert_header(metaTmp, unitsTmp)

            # rename fitting variables to 'Source' to make clear they are coming from the LV fitting
            self.rename_key(metaTmp, unitsTmp, 'pmXStiffness', 'pmXSourceStiffness')
            self.rename_key(metaTmp, unitsTmp, 'pmYStiffness', 'pmYSourceStiffness')
            self.rename_key(metaTmp, unitsTmp, 'aodXStiffness', 'aodXSourceStiffness')
            self.rename_key(metaTmp, unitsTmp, 'aodYStiffness', 'aodYSourceStiffness')
            self.rename_key(metaTmp, unitsTmp, 'pmXCornerFreq', 'pmXSourceCornerFreq')
            self.rename_key(metaTmp, unitsTmp, 'pmYCornerFreq', 'pmYSourceCornerFreq')
            self.rename_key(metaTmp, unitsTmp, 'aodXCornerFreq', 'aodXSourceCornerFreq')
            self.rename_key(metaTmp, unitsTmp, 'aodYCornerFreq', 'aodYSourceCornerFreq')
            self.rename_key(metaTmp, unitsTmp, 'pmXDisplacementSensitivity', 'pmXSourceDisplacementSensitivity')
            self.rename_key(metaTmp, unitsTmp, 'pmYDisplacementSensitivity', 'pmYSourceDisplacementSensitivity')
            self.rename_key(metaTmp, unitsTmp, 'aodXDisplacementSensitivity', 'aodXSourceDisplacementSensitivity')
            self.rename_key(metaTmp, unitsTmp, 'aodYDisplacementSensitivity', 'aodYSourceDisplacementSensitivity')

            # rename variables for the sake of consistency and compatibility with Matlab and because the naming is
            # confusing: samplingRate is actually the acquisition rate since the DAQ card averages the data already
            # the sampling rate should describe the actual time step between data points not something else
            if 'recordingRate' in metaTmp:
                self.rename_key(metaTmp, unitsTmp, 'samplingRate', 'acquisitionRate')
                self.rename_key(metaTmp, unitsTmp, 'recordingRate', 'samplingRate')
                self.rename_key(metaTmp, None, 'nSamples', 'nAcquisitionPerSample')

            # add trial number
            metaTmp['trial'] = self.data.get_trial_number()

            # update dictionaries
            meta.update(metaTmp)
            units.update(unitsTmp)

        # add title string to metadata, used for plots
        self.set_title(meta)

        return meta, units

    def get_data(self):
        """
        Return the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.data:
            raise ValueError('No data file given.')

        # read the data and column headers from file
        columnHeader, data = self.data.get_data()
        # convert the column headers to a standardized format
        columnHeader = self.convert_columns(columnHeader)
        # convert the data to a standardized format
        data = self.convert_data(columnHeader, data)
        return data

    def get_psd(self):
        """
        Return the PSD of the thermal calibration of the experiment as computed by LabView.

        Returns:
            :class:`pandas.DataFrame`
        """

        # read psd file which also contains the fitting
        data = self.read_psd()
        # ignore the fitting
        titles = [title for title, column in data.iteritems() if not title.endswith('Fit')]
        return data[titles]

    def get_psd_fit(self):
        """
        Return the LabView fit of the Lorentzian to the PSD.

        Returns:
            :class:`pandas.DataFrame`
        """

        # the fit is in the psd file
        data = self.read_psd()
        # only choose frequency and fit columns
        titles = [title for title, column in data.iteritems() if title.endswith('Fit') or title == 'f']
        return data[titles]

    def get_ts(self):
        """
        Return the time series recorded for thermal calibration.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.ts:
            raise ValueError('No time series file given.')

        columnHeader, data = self.ts.get_data()
        columnHeader = self.convert_columns(columnHeader)
        data = self.convert_data(columnHeader, data)
        return data

    def read_psd(self):
        """
        Read the PSD file given by LabView which actually contains the PSD and the LabView fit to it.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.psd:
            raise ValueError('No PSD file given.')

        # read the psd
        columnHeader, data = self.psd.get_data()
        # convert column titles to standardized format
        columnHeader = self.convert_columns(columnHeader)
        # convert data to correct format
        data = self.convert_data(columnHeader, data)
        return data


    def set_title(self, meta):
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
            title += meta['trial']
        except KeyError:
            pass

        meta['title'] = title.strip()

    def convert_header(self, header, columnUnits=None):
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
            units = c.UnitDict(meta['units'])
            # insert columnUnits if present
            if columnUnits:
                units.update(columnUnits)
            meta = c.MetaDict(meta['meta'])
        else:
            meta = c.MetaDict()
            units = c.UnitDict()
            # TODO write test for it
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
                if TxtSourceMpi.is_ignored_header(line):
                    continue
                # perform regular expression search
                res = regex.search(line)

                # no match or empty name or value? go to next line
                if not res or res.group('name') is None or res.group('value') is None:
                    continue

                key = TxtSourceMpi.get_standard_identifier(res.group('name'))
                value = TxtSourceMpi.get_value_type(key, res.group('value').strip())
                meta[key] = value
                if not res.group('unit') is None:
                    units[key] = res.group('unit').strip()
                elif not res.group('unit2') is None:
                    units[key] = res.group('unit2').strip()

            # insert units from column headers if present
            if columnUnits:
                # they need to be checked for standardized identifier before being added
                units.update(self.convert_columns(columnUnits))

            # ensure bead diameter, tweebot files have radius
            if self.get_standard_identifier('pmBeadRadius') in meta:
                # using rename_key here to make sure get_standard_identifier is called on key names
                # useful when renaming key in the future
                self.rename_key(meta, None, 'pmBeadRadius', 'pmBeadDiameter')
                meta[self.get_standard_identifier('pmBeadDiameter')] *= 2
                self.rename_key(meta, None, 'aodBeadRadius', 'aodBeadDiameter')
                meta[self.get_standard_identifier('aodBeadDiameter')] *= 2

            # eye candy
            if units['viscosity']:
                units['viscosity'] = units['viscosity'].replace('^2', '²')

        return meta, units

    def convert_data(self, columnHeader, data):
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

    def write_data(self, container, target=None):
        """
        Write experiment data back to a target file. Note that this writes the data in an `UTF-8` encoding and only
        stores the experiment data, not the PSD or time series. Implementing this is not required for a data source
        but used here to convert the header to JSON.

        Args:
            container (:class:`tweezers.TweezerData`): data container
            target (:class:`pathlib.Path`): path where to write the file, if set to ``None`` the input path will be used
        """

        if target is None:
            target = self.data.path
        else:
            if not isinstance(target, Path):
                target = Path(target)

        # we have to store the data here so it is evaluated BEFORE we write to the file, caveat of the laziness...
        header = OrderedDict([('meta', container.meta), ('units', container.units)])
        data = container.data
        with target.open(mode='w', encoding='utf-8') as f:
            f.write(json.dumps(header,
                               indent=4,
                               ensure_ascii=False,
                               sort_keys=True))
            f.write("\n\n#### DATA ####\n\n")

        data.to_csv(path_or_buf=str(target), sep='\t', mode='a', index=False)

    def get_default_meta(self):
        """
        Set default values for metadata and units. This will be overwritten by values in the data files if they exist.

        Returns:
            :class:`tweezers.MetaDict` and :class:`tweezers.UnitDict`
        """

        meta = c.MetaDict()
        units = c.UnitDict()

        meta[self.get_standard_identifier('samplingRateTs')] = 80000
        meta[self.get_standard_identifier('laserDiodeTemp')] = None

        units[self.get_standard_identifier('samplingRateTs')] = 'Hz'
        units[self.get_standard_identifier('laserDiodeTemp')] = '°C'

        return meta, units

    def rename_key(self, meta, units, oldKey, newKey):
        """
        Rename a key in the meta- and units-dictionaries. This uses
        :meth:`tweezers.io.source.TxtFileMpi.get_standard_identifier` for compatibility in case a default identifier
        is renamed.

        Args:
            meta (:class:`tweezers.MetaDict`): meta dictionary
            units (:class:`tweezers.UnitDict`): units dictionary
            oldKey (str): key to be renamed
            newKey (str): new key name

        Returns:

        """

        # for future compatibility reasons, use get_standard_identifier here
        oldKey = self.get_standard_identifier(oldKey)
        newKey = self.get_standard_identifier(newKey)
        meta.replace_key(oldKey, newKey)
        if units:
            units.replace_key(oldKey, newKey)

    def convert_columns(self, struct):
        """
        Convert column header to standardized format. Works with lists or dictionary by replacing the values (list)
        or the keys (dict).

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
                newKey = self.get_standard_identifier(key)
                struct[newKey] = struct.pop(key)
        else:
            for i in range(len(struct)):
                struct[i] = self.get_standard_identifier(struct[i])
        return struct

    @staticmethod
    def get_value_type(key, value):
        """
        Convert the value of a header key from string to the correct format. If no format is given, the input value is
        returned.

        Args:
            key (string): header key to look up
            value (string): value to convert

        Returns:
            converted value
        """

        key_mapper = {
            # general stuff
            'date': lambda x: x.replace('\t', ' '),
            'isDataAveraged': ixo.str_to_bool,
            'nSamples': lambda x: int(float(x)),
            'nSamplesPsd': int,
            'nSamplesTs': int,
            'samplingRate': int,
            'samplingRatePsd': int,
            'timeStepTs': float,
            'recordingRate': int,
            'measurementDuration': float,
            'timeStep': float,
            'deltaTime': float,
            'nBlocks': lambda x: int(float(x)),
            'viscosity': float,

            'laserDiodeTemp': float,
            'laserDiodeHours': float,
            'laserDiodeCurrent': float,

            'errors': lambda x: [int(error) for error in x.split('\t')],

            'startOfMeasurement': int,
            'endOfMeasurement': int,

            # aod variables
            'aodXCornerFreq': float,
            'aodYCornerFreq': float,

            'aodXDetectorOffset': float,
            'aodYDetectorOffset': float,
            'aodZDetectorOffset': float,

            'aodXStiffness': float,
            'aodYStiffness': float,

            'aodXDisplacementSensitivity': float,
            'aodYDisplacementSensitivity': float,

            # pm variables
            'pmXCornerFreq': float,
            'pmYCornerFreq': float,

            'pmXDetectorOffset': float,
            'pmYDetectorOffset': float,
            'pmZDetectorOffset': float,

            'pmXStiffness': float,
            'pmYStiffness': float,

            'pmXDisplacementSensitivity': float,
            'pmYDisplacementSensitivity': float,

            # aod tweebot camera variables
            'andorAodXCenter': float,
            'andorAodYCenter': float,
            'andorAodXRange': float,
            'andorAodYRange': float,

            'ccdAodXCenter': float,
            'ccdAodYCenter': float,
            'ccdAodXRange': float,
            'ccdAodYRange': float,

            # pm tweebot camera variables
            'andorPmXCenter': float,
            'andorPmYCenter': float,
            'andorPmXRange': float,
            'andorPmYRange': float,

            'ccdPmXCenter': float,
            'ccdPmYCenter': float,
            'ccdPmXRange': float,
            'ccdPmYRange': float,

            # bead
            'pmBeadDiameter': float,
            'pmBeadRadius': float,
            'aodBeadDiameter': float,
            'aodBeadRadius': float,

            # andor camera specifics
            'andorXPixelSize': float,
            'andorYPixelSize': float,

            # ccd camera specifics
            'ccdXPixelSize': float,
            'ccdYPixelSize': float,
        }

        if key in key_mapper:
            return key_mapper[key](value)
        else:
            return value

    @staticmethod
    def get_standard_identifier(key):
        """
        Translate a header key to a unique identifier. This is necessary as several versions of header keys are around.

        Args:
            key (str): the key to look up

        Returns:
            str
        """

        # reduce number of variations: strip spaces
        # one could also change everything to lower case but that would decrease readability
        key = key.strip()

        key_mapper = {
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
            'nSamples': 'nSamples',
            'nSamplesPsd': 'nSamplesPsd',
            'nSamplesTs': 'nSamplesTs',

            'sample rate': 'samplingRate',
            'Sample rate (Hz)': 'samplingRate',
            'Sample rate': 'samplingRate',
            'sampleRate.Hz': 'samplingRate',
            'samplingRate': 'samplingRate',
            'samplingRatePsd': 'samplingRatePsd',
            'samplingRateTs': 'samplingRateTs',

            'acquisitionRate': 'acquisitionRate',
            'recordingRate': 'recordingRate',
            'nAcquisitionPerSample': 'nAcquisitionPerSample',

            'rate of while-loop': 'recordingRate',
            'duration of measurement': 'measurementDuration',
            'dt': 'timeStep',
            'timeStep': 'timeStep',
            'timeStepTs': 'timeStepTs',
            'Delta time': 'deltaTime',

            'number of blocks': 'nBlocks',
            'nBlocks': 'nBlocks',

            'Viscosity': 'viscosity',
            'viscosity': 'viscosity',

            'Laser Diode Temp': 'laserDiodeTemp',
            'laserDiodeTemp': 'laserDiodeTemp',
            'Laser Diode Operating Hours': 'laserDiodeHours',
            'Laser Diode Current': 'laserDiodeCurrent',

            'errors': 'errors',
            'start of measurement': 'startOfMeasurement',
            'end of measurement': 'endOfMeasurement',

            # aod variables
            'aodXCornerFreq': 'aodXCornerFreq',
            'aodYCornerFreq': 'aodYCornerFreq',
            'aodXSourceCornerFreq': 'aodXSourceCornerFreq',
            'aodYSourceCornerFreq': 'aodYSourceCornerFreq',
            'AOD horizontal corner frequency': 'aodXCornerFreq',
            'AOD vertical corner frequency': 'aodYCornerFreq',

            'AOD detector horizontal offset': 'aodXDetectorOffset',
            'AOD detector vertical offset': 'aodYDetectorOffset',

            'aodXStiffness': 'aodXStiffness',
            'aodYStiffness': 'aodYStiffness',
            'aodXSourceStiffness': 'aodXSourceStiffness',
            'aodYSourceStiffness': 'aodYStiffness',
            'AOD horizontal trap stiffness': 'aodXStiffness',
            'AOD vertical trap stiffness': 'aodYStiffness',

            'aodXDisplacementSensitivity': 'aodXDisplacementSensitivity',
            'aodYDisplacementSensitivity': 'aodYDisplacementSensitivity',
            'aodXSourceDisplacementSensitivity': 'aodXSourceDisplacementSensitivity',
            'aodYSourceDisplacementSensitivity': 'aodYSourceDisplacementSensitivity',
            'AOD horizontal OLS': 'aodXDisplacementSensitivity',
            'AOD vertical OLS': 'aodYDisplacementSensitivity',

            # pm variables
            'pmXCornerFreq': 'pmXCornerFreq',
            'pmYCornerFreq': 'pmYCornerFreq',
            'pmXSourceCornerFreq': 'pmXSourceCornerFreq',
            'pmYSourceCornerFreq': 'pmYSourceCornerFreq',
            'PM horizontal corner frequency': 'pmXCornerFreq',
            'PM vertical corner frequency': 'pmYCornerFreq',

            'PM detector horizontal offset': 'pmXDetectorOffset',
            'PM detector vertical offset': 'pmYDetectorOffset',

            'pmXStiffness': 'pmXStiffness',
            'pmYStiffness': 'pmYStiffness',
            'pmXSourceStiffness': 'pmXSourceStiffness',
            'pmYSourceStiffness': 'pmYSourceStiffness',
            'PM horizontal trap stiffness': 'pmXStiffness',
            'PM vertical trap stiffness': 'pmYStiffness',

            'pmXDisplacementSensitivity': 'pmXDisplacementSensitivity',
            'pmYDisplacementSensitivity': 'pmYDisplacementSensitivity',
            'pmXSourceDisplacementSensitivity': 'pmXSourceDisplacementSensitivity',
            'pmYSourceDisplacementSensitivity': 'pmYSourceDisplacementSensitivity',
            'PM horizontal OLS': 'pmXDisplacementSensitivity',
            'PM vertical OLS': 'pmYDisplacementSensitivity',

            # aod tweebot variables
            'AOD detector x offset': 'aodXDetectorOffset',
            'AOD detector y offset': 'aodYDetectorOffset',

            'AOD trap stiffness x': 'aodXStiffness',
            'AOD trap stiffness y': 'aodYStiffness',

            'xStiffnessT2.pNperNm': 'aodXStiffness',
            'yStiffnessT2.pNperNm': 'aodYStiffness',

            'AOD trap distance conversion x': 'aodXDisplacementSensitivity',
            'AOD trap distance conversion y': 'aodYDisplacementSensitivity',

            'xDistConversionT2.VperNm': 'aodXDisplacementSensitivity',
            'yDistConversionT2.VperNm': 'aodYDisplacementSensitivity',

            'xCornerFreqT2.Hz': 'aodXCornerFreq',
            'xCornerFreqT2': 'aodXCornerFreq',
            'yCornerFreqT2.Hz': 'aodYCornerFreq',
            'yCornerFreqT2': 'aodYCornerFreq',

            'xOffsetT2.V': 'aodXDetectorOffset',
            'yOffsetT2.V': 'aodYDetectorOffset',
            'zOffsetT2.V': 'aodZDetectorOffset',

            # pm tweebot variables
            'PM detector x offset': 'pmXDetectorOffset',
            'PM detector y offset': 'pmYDetectorOffset',

            'PM trap stiffness x': 'pmXStiffness',
            'PM trap stiffness y': 'pmYStiffness',

            'xStiffnessT1.pNperNm': 'pmXStiffness',
            'yStiffnessT1.pNperNm': 'pmYStiffness',

            'PM trap distance conversion x': 'pmXDisplacementSensitivity',
            'PM trap distance conversion y': 'pmYDisplacementSensitivity',

            'xDistConversionT1.VperNm': 'pmXDisplacementSensitivity',
            'yDistConversionT1.VperNm': 'pmYDisplacementSensitivity',

            'xCornerFreqT1.Hz': 'pmXCornerFreq',
            'xCornerFreqT1': 'pmXCornerFreq',
            'yCornerFreqT1.Hz': 'pmYCornerFreq',
            'yCornerFreqT1': 'pmYCornerFreq',

            'xOffsetT1.V': 'pmXDetectorOffset',
            'xOffsetT1': 'pmXDetectorOffset',
            'yOffsetT1.V': 'pmYDetectorOffset',
            'yOffsetT1': 'pmYDetectorOffset',
            'zOffsetT1.V': 'pmZDetectorOffset',

            # aod tweebot camera variables
            'AOD ANDOR center x': 'andorAodXCenter',
            'AOD ANDOR center y': 'andorAodYCenter',
            'AOD ANDOR range x': 'andorAodXRange',
            'AOD ANDOR range y': 'andorAodYRange',

            'AOD CCD center x': 'ccdAodXCenter',
            'AOD CCD center y': 'ccdAodYCenter',
            'AOD CCD range x': 'ccdAodXRange',
            'AOD CCD range y': 'ccdAodYRange',

            # pm tweebot camera variables
            'PM ANDOR center x': 'andorPmXCenter',
            'PM ANDOR center y': 'andorPmYCenter',
            'PM ANDOR range x': 'andorPmXRange',
            'PM ANDOR range y': 'andorPmYRange',

            'PM CCD center x': 'ccdXPmCenter',
            'PM CCD center y': 'ccdYPmCenter',
            'PM CCD range x': 'ccdXPmRange',
            'PM CCD range y': 'ccdYPmRange',

            # bead
            'PM bead diameter': 'pmBeadDiameter',
            'diameterT1.um': 'pmBeadDiameter',
            'pmBeadDiameter': 'pmBeadDiameter',
            'PM bead radius': 'pmBeadRadius',
            'pmBeadRadius': 'pmBeadRadius',

            'AOD bead diameter': 'aodBeadDiameter',
            'diameterT2.um': 'aodBeadDiameter',
            'aodBeadDiameter': 'aodBeadDiameter',
            'AOD bead radius': 'aodBeadRadius',
            'aodBeadRadius': 'aodBeadRadius',

            # andor camera specifics
            'ANDOR pixel size x': 'andorXPixelSize',
            'ANDOR pixel size y': 'andorYPixelSize',

            # ccd camera specifics
            'CCD pixel size x': 'ccdXPixelSize',
            'CCD pixel size y': 'ccdYPixelSize'
        }

        return key_mapper[key]

    @staticmethod
    def is_ignored_header(line):
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
