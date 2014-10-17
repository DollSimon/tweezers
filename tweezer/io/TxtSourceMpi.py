from pathlib import Path
import json
import re
import pandas as pd
from io import StringIO
import numpy as np
from collections import OrderedDict
from .TxtFileMpi import TxtFileMpi
from .BaseSource import BaseSource

import tweezer as c
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
            :class:`tweezer.MetaDict`
        """

        # keep variables local so they are not stored in memory
        meta, units = self.get_default_meta()

        # check each available file for header information
        # sequence is important since later calls overwrite earlier ones so if a header is present in "psd" and
        # "data", the value from "data" will be returned
        if self.ts:
            metaTmp, unitsTmp = self.ts.get_header()
            metaTmp, unitsTmp = self.convert_header(metaTmp, unitsTmp)
            meta.update(metaTmp)
            units.update(unitsTmp)

            # make sure we don't override important stuff that by accident has the same name
            self.rename_key(meta, units, 'nSamples', 'nSamplesTs')
            self.rename_key(meta, units, 'timeStep', 'timeStepTs')

        if self.psd:
            metaTmp, unitsTmp = self.psd.get_header()
            # adjust psd column headers in unit dict (if present)
            unitsTmp = self.convert_psd_columns(unitsTmp)
            metaTmp, unitsTmp = self.convert_header(metaTmp, unitsTmp)
            meta.update(metaTmp)
            units.update(unitsTmp)

            # make sure we don't override important stuff that by accident has the same name
            self.rename_key(meta, units, 'nSamples', 'nSamplesPsd')
            self.rename_key(meta, units, 'samplingRate', 'samplingRatePsd')

        if self.data:
            metaTmp, unitsTmp = self.data.get_header()
            metaTmp, unitsTmp = self.convert_header(metaTmp, unitsTmp)
            meta.update(metaTmp)
            units.update(unitsTmp)
            meta['trial'] = self.data.get_trial_number()

            # rename fitting variables to 'Source' to make clear they are coming from the LV fitting
            self.rename_key(meta, units, 'pmStiffnessX', 'pmStiffnessXSource')
            self.rename_key(meta, units, 'pmStiffnessY', 'pmStiffnessYSource')
            self.rename_key(meta, units, 'aodStiffnessX', 'aodStiffnessXSource')
            self.rename_key(meta, units, 'aodStiffnessY', 'aodStiffnessYSource')
            self.rename_key(meta, units, 'pmCornerFreqX', 'pmCornerFreqXSource')
            self.rename_key(meta, units, 'pmCornerFreqY', 'pmCornerFreqYSource')
            self.rename_key(meta, units, 'aodCornerFreqX', 'aodCornerFreqXSource')
            self.rename_key(meta, units, 'aodCornerFreqY', 'aodCornerFreqYSource')

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

        columnHeader, data = self.data.get_data()
        data = self.convert_data(columnHeader, data)
        return data

    def get_psd(self):
        """
        Return the PSD of the thermal calibration of the experiment.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.psd:
            raise ValueError('No PSD file given.')

        columnHeader, data = self.psd.get_data()
        # convert PSD column titles to standardized format
        columnHeader = self.convert_psd_columns(columnHeader)
        data = self.convert_data(columnHeader, data)
        return data

    def get_ts(self):
        """
        Return the time series recorded for thermal calibration.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.ts:
            raise ValueError('No time series file given.')

        columnHeader, data = self.ts.get_data()
        data = self.convert_data(columnHeader, data)
        return data

    def set_title(self, meta):
        """
        Set the 'title' key in the metadata dictionary based on date and trial number if they are available. This
        string is e.g. used for plots.

        Args:
            meta

        Returns:
            :class:`tweezer.MetaDict`
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
            :class:`tweezer.MetaDict` and :class:`tweezer.UnitDict`
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
            regex = re.compile('^(# )?(?P<name>[^(:\d]*)\s?(\((?P<unit>[^:]*?)\))?(:|\s)(?P<value>\s?.+?|[^\s]+)(?! PM)(?P<unit2>\s\D+)?$')
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
                units.update(columnUnits)

            # eye candy
            if units['viscosity']:
                units['viscosity'] = units['viscosity'].replace('^2', '²')

        return meta, units

    def convert_psd_columns(self, struct):
        """
        Convert PSD-file column header to standardized format. Works with lists or dictionary by replacing the keys.

        Args:
            columnHeader (:class:`list` of :class:`str`)

        Returns:
            :class:`list` of :class:`str`
        """

        lookup = {'freq': 'f',
                  'PSDPMx': 'PMx',
                  'PSDPMy': 'PMy',
                  'PSDAODx': 'AODx',
                  'PSDAODy': 'AODy',
                  'FitPMx': 'fitPMx',
                  'FitPMy': 'fitPMy',
                  'FitAODx': 'fitAODx',
                  'FitAODy': 'fitAODy'
        }

        if type(struct) == 'dict':
            for key in struct:
                if key in lookup:
                    struct[lookup[key]] = struct.pop(key)
        else:
            for i in range(len(struct)):
                if struct[i] in lookup:
                    struct[i] = lookup[struct[i]]
        return struct

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
            container (:class:`tweezer.TweezerData`): data container
            target (:class:`pathlib.Path`): path where to write the file, if set to ``None`` the input path will be used
        """

        if target is None:
            target = self.data
        else:
            if not isinstance(target, Path):
                target = Path(target)

        with target.open(mode='w', encoding='utf-8') as f:
            f.write(json.dumps(OrderedDict([('meta', container.meta), ('units', container.units)]),
                               indent=4,
                               ensure_ascii=False))
            f.write("\n\n#### DATA ####\n\n")

        container.data.to_csv(path_or_buf=target.__str__(), sep='\t', mode='a', index=False)

    def get_default_meta(self):
        """
        Set default values for metadata and units. This will be overwritten by values in the data files if they exist.

        Returns:
            :class:`tweezer.MetaDict` and :class:`tweezer.UnitDict`
        """

        meta = c.MetaDict()
        units = c.UnitDict()

        meta[self.get_standard_identifier('samplingRateTs')] = 80000

        units[self.get_standard_identifier('samplingRateTs')] = 'Hz'

        return meta, units

    def rename_key(self, meta, units, oldKey, newKey):
        """
        Rename a key in the meta- and units-dictionaries. This uses
        :meth:`tweezer.io.source.TxtFileMpi.get_standard_identifier` for compatibility in case a default identifier
        is renamed.

        Args:
            meta (:class:`tweezer.MetaDict`): meta dictionary
            units (:class:`tweezer.UnitDict`): units dictionary
            oldKey (str): key to be renamed
            newKey (str): new key name

        Returns:

        """

        # for future compatibility reasons, use get_standard_identifier here
        oldKey = self.get_standard_identifier(oldKey)
        newKey = self.get_standard_identifier(newKey)
        meta.replace_key(oldKey, newKey)
        units.replace_key(oldKey, newKey)

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

            # aod variables
            'aodCornerFreqX': float,
            'aodCornerFreqY': float,

            'aodDetectorOffsetX': float,
            'aodDetectorOffsetY': float,
            'aodDetectorOffsetZ': float,

            'aodStiffnessX': float,
            'aodStiffnessY': float,

            'aodDisplacementSensitivityX': float,
            'aodDisplacementSensitivityY': float,

            # pm variables
            'pmCornerFreqX': float,
            'pmCornerFreqY': float,

            'pmDetectorOffsetX': float,
            'pmDetectorOffsetY': float,
            'pmDetectorOffsetZ': float,

            'pmStiffnessX': float,
            'pmStiffnessY': float,

            'pmDisplacementSensitivityX': float,
            'pmDisplacementSensitivityY': float,

            # aod tweebot camera variables
            'andorAodCenterX': float,
            'andorAodCenterY': float,
            'andorAodRangeX': float,
            'andorAodRangeY': float,

            'ccdAodCenterX': float,
            'ccdAodCenterY': float,
            'ccdAodRangeX': float,
            'ccdAodRangeY': float,

            # pm tweebot camera variables
            'andorPmCenterX': float,
            'andorPmCenterY': float,
            'andorPmRangeX': float,
            'andorPmRangeY': float,

            'ccdPmCenterX': float,
            'ccdPmCenterY': float,
            'ccdPmRangeX': float,
            'ccdPmRangeY': float,

            # bead
            'pmBeadDiameter': float,
            'aodBeadDiameter': float,

            # andor camera specifics
            'andorPixelSizeX': float,
            'andorPixelSizeY': float,

            # ccd camera specifics
            'ccdPixelSizeX': float,
            'ccdPixelSizeY': float,
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
            # general stuff
            'Date of Experiment': 'date',
            'measurement starttime': 'startTime',
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
            'Laser Diode Operating Hours': 'laserDiodeHours',
            'Laser Diode Current': 'laserDiodeCurrent',

            'errors': 'errors',
            'start of measurement': 'startOfMeasurement',
            'end of measurement': 'endOfMeasurement',

            # aod variables
            'aodCornerFreqX': 'aodCornerFreqX',
            'aodCornerFreqY': 'aodCornerFreqY',
            'aodCornerFreqXSource': 'aodCornerFreqXSource',
            'aodCornerFreqYSource': 'aodCornerFreqYSource',
            'AOD horizontal corner frequency': 'aodCornerFreqX',
            'AOD vertical corner frequency': 'aodCornerFreqY',

            'AOD detector horizontal offset': 'aodDetectorOffsetX',
            'AOD detector vertical offset': 'aodDetectorOffsetY',

            'aodStiffnessX': 'aodStiffnessX',
            'aodStiffnessY': 'aodStiffnessY',
            'aodStiffnessXSource': 'aodStiffnessXSource',
            'aodStiffnessYSource': 'aodStiffnessYSource',
            'AOD horizontal trap stiffness': 'aodStiffnessX',
            'AOD vertical trap stiffness': 'aodStiffnessY',

            'AOD horizontal OLS': 'aodDisplacementSensitivityX',
            'AOD vertical OLS': 'aodDisplacementSensitivityY',

            # pm variables
            'pmCornerFreqX': 'pmCornerFreqX',
            'pmCornerFreqY': 'pmCornerFreqY',
            'pmCornerFreqXSource': 'pmCornerFreqXSource',
            'pmCornerFreqYSource': 'pmCornerFreqYSource',
            'PM horizontal corner frequency': 'pmCornerFreqX',
            'PM vertical corner frequency': 'pmCornerFreqY',

            'PM detector horizontal offset': 'pmDetectorOffsetX',
            'PM detector vertical offset': 'pmDetectorOffsetY',

            'pmStiffnessX': 'pmStiffnessX',
            'pmStiffnessY': 'pmStiffnessY',
            'pmStiffnessXSource': 'pmStiffnessXSource',
            'pmStiffnessYSource': 'pmStiffnessYSource',
            'PM horizontal trap stiffness': 'pmStiffnessX',
            'PM vertical trap stiffness': 'pmStiffnessY',

            'PM horizontal OLS': 'pmDisplacementSensitivityX',
            'PM vertical OLS': 'pmDisplacementSensitivityY',

            # aod tweebot variables
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

            'xCornerFreqT2.Hz': 'aodCornerFreqX',
            'xCornerFreqT2': 'aodCornerFreqX',
            'yCornerFreqT2.Hz': 'aodCornerFreqY',
            'yCornerFreqT2': 'aodCornerFreqY',

            'xOffsetT2.V': 'aodDetectorOffsetX',
            'yOffsetT2.V': 'aodDetectorOffsetY',
            'zOffsetT2.V': 'aodDetectorOffsetZ',

            # pm tweebot variables
            'PM detector x offset': 'pmDetectorOffsetX',
            'PM detector y offset': 'pmDetectorOffsetY',

            'PM trap stiffness x': 'pmStiffnessX',
            'PM trap stiffness y': 'pmStiffnessY',

            'xStiffnessT1.pNperNm': 'pmStiffnessX',
            'yStiffnessT1.pNperNm': 'pmStiffnessY',

            'PM trap distance conversion x': 'pmDisplacementSensitivityX',
            'PM trap distance conversion y': 'pmDisplacementSensitivityY',

            'xDistConversionT1.VperNm': 'pmDisplacementSensitivityX',
            'yDistConversionT1.VperNm': 'pmDisplacementSensitivityY',

            'xCornerFreqT1.Hz': 'pmCornerFreqX',
            'xCornerFreqT1': 'pmCornerFreqX',
            'yCornerFreqT1.Hz': 'pmCornerFreqY',
            'yCornerFreqT1': 'pmCornerFreqY',

            'xOffsetT1.V': 'pmDetectorOffsetX',
            'xOffsetT1': 'pmDetectorOffsetX',
            'yOffsetT1.V': 'pmDetectorOffsetY',
            'yOffsetT1': 'pmDetectorOffsetY',
            'zOffsetT1.V': 'pmDetectorOffsetZ',

            # aod tweebot camera variables
            'AOD ANDOR center x': 'andorAodCenterX',
            'AOD ANDOR center y': 'andorAodCenterY',
            'AOD ANDOR range x': 'andorAodRangeX',
            'AOD ANDOR range y': 'andorAodRangeY',

            'AOD CCD center x': 'ccdAodCenterX',
            'AOD CCD center y': 'ccdAodCenterY',
            'AOD CCD range x': 'ccdAodRangeX',
            'AOD CCD range y': 'ccdAodRangeY',

            # pm tweebot camera variables
            'PM ANDOR center x': 'andorPmCenterX',
            'PM ANDOR center y': 'andorPmCenterY',
            'PM ANDOR range x': 'andorPmRangeX',
            'PM ANDOR range y': 'andorPmRangeY',

            'PM CCD center x': 'ccdPmCenterX',
            'PM CCD center y': 'ccdPmCenterY',
            'PM CCD range x': 'ccdPmRangeX',
            'PM CCD range y': 'ccdPmRangeY',

            # bead
            'PM bead diameter': 'pmBeadDiameter',
            'diameterT1.um': 'pmBeadDiameter',

            'AOD bead diameter': 'aodBeadDiameter',
            'diameterT2.um': 'aodBeadDiameter',

            # andor camera specifics
            'ANDOR pixel size x': 'andorPixelSizeX',
            'ANDOR pixel size y': 'andorPixelSizeY',

            # ccd camera specifics
            'CCD pixel size x': 'ccdPixelSizeX',
            'CCD pixel size y': 'ccdPixelSizeY'
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
            '# results thermal calibration:'
        ]

        if line in ignoredLines:
            return True
        else:
            return False
