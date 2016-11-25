from pathlib import Path
import json
from collections import OrderedDict
import pandas as pd
import numpy as np
import re

from .BaseSource import BaseSource
import tweezers as t
from tweezers.ixo.collections import IndexedOrderedDict
from tweezers.ixo.io import DataFrameJsonDecoder, DataFrameJsonEncoder


class TxtBiotecSource(BaseSource):
    """
    Data source for *.txt files from the Biotec tweezers.
    """
    # todo: get segment method to only read segment data

    # hold paths to respective files
    header = None
    psd = None
    data = None
    analysis = None
    ts = None
    # path to data, not correct if files sit in different folders
    path = None

    def __init__(self, data=None, analysis=None, psd=None, ts=None, **kwargs):
        """
        Constructor for TxtBiotecSource

        Args:
            data (:class:`pathlib.Path`): path to data file to read, if the input is of a different type, it is given to
                                           :class:`pathlib.Path` to try to create an instance
            psd (:class:`pathlib.Path`): path to psd file to read, similar to `data` input
        """

        super().__init__(**kwargs)

        # order is important here for the header file
        if ts:
            self.ts = Path(ts)
            self.header = self.ts

        if psd:
            self.psd = Path(psd)
            self.header = self.psd

        if data:
            self.data = Path(data)
            self.header = self.data

        if analysis:
            self.analysis = Path(analysis)

        self.path = self.header.parent

    @classmethod
    def fromIdDict(cls, idDict):
        """
        Creates a data source from a given experiment ID and the associated files.

        Args:
            idDict (dict): with keys `data`, `ts`, `psd` etc. whose values are the
                            full paths to the corresponding files.

        Returns:
            :class:`tweezers.io.TxtBiotecSource`
        """

        return cls(**idDict)

    @staticmethod
    def isDataFile(path):
        """
        Checks if a given file is a valid data file and returns its ID and type

        Args:
            path (:class:`pathlib.Path`): file to check

        Returns:
            :class:`dict` with `id` and `type`
        """

        pPath = Path(path)
        m = re.match('^(?P<id>[0-9\-_]{19}.*)\s(?P<type>[a-zA-Z]+)\.txt$', pPath.name)
        if m:
            res = {'id': m.group('id'), 'type': m.group('type').lower()}
            return res
        else:
            return {}

    @staticmethod
    def getAllIds(path):
        """
        Get a list of all IDs and their files that are at the given path and its subfolders.

        Args:
            path (:class:`pathlib.Path`): root path for searching

        Returns:
            :class:`dir`
        """

        pPath = Path(path)

        ids = {}
        for obj in pPath.iterdir():
            if obj.is_dir():
                # if obj is a directory enter it recursively
                m = TxtBiotecSource.getAllIds(obj)
                # merge result to ID list
                for idStr, info in m.items():
                    if idStr not in ids.keys():
                        ids[idStr] = {}
                    for typeStr, filePath in info.items():
                        ids[idStr][typeStr] = filePath
            else:
                # if it is a file, check if it is a data file
                m = TxtBiotecSource.isDataFile(obj)
                # append result to ID list
                if m:
                    if m['id'] not in ids.keys():
                        ids[m['id']] = {}
                    ids[m['id']][m['type']] = obj

        return ids

    def getMetadata(self):
        """
        Return the metadata of the experiment.

        Returns:
            :class:`tweezers.MetaDict` and :class:`tweezers.UnitDict`
        """

        if not self.header:
            raise ValueError('No header file given (probably no file given at all).')

        headerStr = ''
        with self.header.open(encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    break
                else:
                    headerStr += line

        header = json.loads(headerStr, object_pairs_hook=OrderedDict)
        units = t.UnitDict(header.pop('units'))
        meta = t.MetaDict(header)

        # add column header units
        colHeaders, colUnits = self.readColumnTitles(self.header)
        units.update(colUnits)

        # add id from header file name
        idDict = self.isDataFile(self.header)
        meta['id'] = idDict['id']

        # add trap names
        meta['traps'] = meta.subDictKeys()

        return meta, units

    def getPsd(self):
        """
        Returns the power spectral density (PSD) used for the calibration of the experiment by the data source.

        Returns:
            :class:`pandas.DataFrame`
        """

        # get file content
        psd = self.readToDataframe(self.psd)
        # ignore fit columns
        cols = [s for s in psd.columns if not s.lower().endswith('fit')]
        psd = psd[cols]
        return psd

    def getPsdFit(self):
        """
         Returns the fit to the PSD as performed by the data source.

        Returns:
            :class:`pandas.DataFrame`
        """

        # get file content
        psd = self.readToDataframe(self.psd)
        # ignore non-fit columns
        cols = [s for s in psd.columns if s.lower().endswith('fit')]
        psd = psd[['f'] + cols]
        return psd

    def getTs(self):
        """
        Returns the time series recorded for the thermal calibration of the experiment. This is used to compute the
        PSD.

        Returns:
            :class:`pandas.DataFrame`
        """

        ts = self.readToDataframe(self.ts)
        ts.rename(columns={'pmXDiff': 'pmX', 'pmYDiff': 'pmY', 'aodXDiff': 'aodX', 'aodYDiff': 'aodY'},
                  inplace=True)
        return ts

    def getData(self):
        """
        Return the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        data = self.readToDataframe(self.data)
        return data

    def getDataSegment(self, tmin, tmax, chunkN=10000):
        # todo docstring
        # todo fix reading endinge in read_csv to 'c' when switching to pandas 0.19

        # read required information about file and create the chunked iterator
        colHeaders, colUnits = self.readColumnTitles(self.data)
        nHeaderLine = self.findHeaderLine(self.data)
        # read the first data line to allow conversion between absolute and relative time
        firstLine = pd.read_csv(self.data, sep='\t', skiprows=nHeaderLine + 1, header=None,
                                names=colHeaders, nrows=1)
        t0 = firstLine.time.iloc[0]
        # consider adding dtype=np.float64, when switching to engine='c'
        iterCsv = pd.read_csv(self.data, sep='\t', skiprows=nHeaderLine+1, header=None,
                              names=colHeaders, iterator=True, chunksize=chunkN, engine='python')

        # read the chunks into memory if they are within the requested limits
        df = []
        for chunk in iterCsv:
            if chunk['time'].iloc[0] - t0 > tmax:
                # stop reading if the upper time limit was reached
                iterCsv.close()
                break
            selection = chunk[(chunk['time'] - t0 >= tmin) & (chunk['time'] - t0 <= tmax)]
            df.append(selection)

        # return concatenated dataframe with all the requested data
        return pd.concat(df, ignore_index=True)

    def postprocessData(self, meta, units, data):
        """
        Modify the time array to use relative times (but keep the absolute time) and calculate forces.

        Args:
            meta: :class:`tweezers.MetaDict`
            units: :class:`tweezers.UnitDict`
            data: :class:`pandas.DataFrame`

        Returns:
            meta, units, data
        """

        # create relative time column but keep absolute time
        data['absTime'] = data.time.copy()
        data.loc[:, 'time'] -= data.loc[0, 'time']
        units['absTime'] = 's'

        # calculate force per trap and axis
        for trap in meta['traps']:
            m = meta[trap]
            data[trap + 'Force'] = (data[trap + 'Diff'] - m['zeroOffset']) * m['forceSensitivity']
            units[trap + 'Force'] = 'pN'

        # invert PM force, is not as expected in the raw data
        data.pmYForce = -data.pmYForce

        # calculate mean force per axis, only meaningful for two traps
        data['xForce'] = (data.pmXForce + data.aodXForce) / 2
        data['yForce'] = (data.pmYForce - data.aodYForce) / 2

        units['xForce'] = 'pN'
        units['yForce'] = 'pN'

        # calculate bead distance centre to centre, only meaningful for two trapped beads
        data['distance'] = np.sqrt((data.pmYBead - data.aodYBead)**2 + (data.pmXBead - data.aodXBead)**2)
        units['distance'] = 'nm'

        return meta, units, data

    def getAnalysisDict(self):
        #Todo docstring

        if not self.analysis:
            return IndexedOrderedDict()

        with self.analysis.open(mode='r', encoding='utf-8') as f:
            analysisDict = json.load(f, object_pairs_hook=IndexedOrderedDict, cls=DataFrameJsonDecoder)
        return analysisDict

    def writeAnalysisDict(self, analysisDict):
        # todo docstring

        # build filename if it does not exist
        if not self.analysis:
            self.analysis = self.data.parent.joinpath(self.data.name.replace('DATA', 'ANALYSIS'))

        # write data to file
        jsonStr = json.dumps(analysisDict, indent=4, cls=DataFrameJsonEncoder)
        with self.analysis.open(mode='w', encoding='utf-8') as f:
            f.write(jsonStr)

    def getAnalysis(self):
        """
        Return the analysis data.

        Returns:
            :class:`collections.OrderedDict`
        """

        return self.getAnalysisDict().get('analysis', OrderedDict())

    def writeAnalysis(self, analysis, segment=None):
        # todo: docstring

        analysisDict = self.getAnalysisDict()

        # should we only update the segment?
        if segment is not None:
            analysisDict['segments'][segment] = analysis
            # remove the general analysis keys
            for key in analysisDict['analysis'].keys():
                analysisDict['segments'][segment].pop(key, None)
        else:
            # sort analysis keys and store in the proper dictionary
            analysisDict['analysis'] = OrderedDict(sorted(analysis.items()))

        self.writeAnalysisDict(analysisDict)

    def getSegments(self):
        # todo docstring
        return self.getAnalysisDict().get('segments', IndexedOrderedDict())

    def writeSegments(self, segments):
        #todo docstring

        analysisDict = self.getAnalysisDict()
        analysisDict['segments'] = segments
        self.writeAnalysisDict(analysisDict)


    def findHeaderLine(self, file):
        """
        Find the line number of the first header line, searches for '### DATA ###'

        Args:
            file (:class:`pathlib.Path`): path to file
        """

        n = 0
        with file.open(encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    break
                else:
                    n += 1

        return n + 2

    def readColumnTitles(self, file):
        """
        Read the column titles and if available their units. They are expected to be given as 'f [Hz]', separated by
        tabstops.

        Args:
            file: (:class:`pathlib.Path`): path to file

        Returns:
            list: column header names
            :class:`tweezers.UnitDict`: units dictionary with available column units
        """

        # read header line
        nHeaderLine = self.findHeaderLine(file)
        with file.open(encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i == nHeaderLine:
                    headerLine = line
                    break

        # get column title names with units
        regex = re.compile('(\w+)(?:\s\[(\w*)\])?')
        header = regex.findall(headerLine)

        # store them in a UnitDict
        colHeaders = []
        colUnits = t.UnitDict()
        for (colHeader, unit) in header:
            colHeaders.append(colHeader)
            if unit:
                colUnits[colHeader] = unit

        return colHeaders, colUnits

    def readToDataframe(self, file):
        """
        Read the given file into a :class:`pandas.DataFrame` and skip the header lines.

        Args:
            file (:class:`pathlib.Path`): path to file

        Returns:
            :class:`pandas.DataFrame`
        """

        colHeaders, colUnits = self.readColumnTitles(file)
        nHeaderLine = self.findHeaderLine(file)
        df = pd.read_csv(str(file), sep='\t', dtype=np.float64, skiprows=nHeaderLine+1, header=None,
                         names=colHeaders, engine='c')
        return df
