from pathlib import Path
import json
from collections import OrderedDict
import pandas as pd
import numpy as np
import re

from .BaseSource import BaseSource
import tweezers as t
from tweezers.collections import TweezersCollection


class TxtBiotecSource(BaseSource):
    """
    Data source for \*.txt files from the Biotec tweezers.
    """

    # hold paths to respective files
    header = None
    psd = None
    data = None
    ts = None
    # path to data, not correct if files sit in different folders
    path = None

    def __init__(self, data=None, analysis=None, psd=None, ts=None, screenshot=None, **kwargs):
        """
        Args:
            data (:class:`pathlib.Path`): path to data file to read, if the input is of a different type, it is given to
                                           :class:`pathlib.Path` to try to create an instance
            analysis (:class:`pathlib.Path`): path to analysis file
            psd (:class:`pathlib.Path`): path to psd file
            ts (:class:`pathlib.Path`): path to ts file
            screenshot (:class:`pathlib.Path`): path to screenshot file
            kwargs: forwared to super class
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
        if screenshot:
            self.screenshot = Path(screenshot)

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
            `dict` with ``id`` and ``type``
        """

        pPath = Path(path)
        m = re.match('^(?P<beadId>[0-9\-_]{19}.*#\d{3})(?P<trial>-\d{3})?\s(?P<type>[a-zA-Z]+)\.[a-zA-Z]{3}$',
                     pPath.name)
        if m:
            ide = None
            if m.group('trial'):
                ide = '{}{}'.format(m.group('beadId'), m.group('trial'))
            res = {'beadId': m.group('beadId'),
                   'id': ide,
                   'type': m.group('type').lower(),
                   'path': pPath}
            return res
        else:
            return False

    @staticmethod
    def getAllFiles(path):
        """
        Return a recursive list of all valid data files within a given path.

        Args:
            path (:class:`pathlib.Path`): root path to search for valid data files

        Returns:
            `list` of `dict`
        """

        pPath = Path(path)
        files = []

        for obj in pPath.iterdir():
            if obj.is_dir():
                subFiles = TxtBiotecSource.getAllFiles(obj)
                files += subFiles
            else:
                m = TxtBiotecSource.isDataFile(obj)
                if m:
                    files.append(m)
        return files

    @staticmethod
    def getAllIds(path):
        """
        Get a list of all IDs and their files that are at the given path and its subfolders.

        Args:
            path (:class:`pathlib.Path`): root path for searching

        Returns:
            `dict`
        """

        pPath = Path(path)

        # get a list of all files and their properties
        files = TxtBiotecSource.getAllFiles(pPath)
        ids = TweezersCollection()
        sharedFiles = {}

        # sort files in sharedFiles and actual data files that belong to an individual trial
        for el in files:
            if el['id']:
                if el['beadId'] not in ids.keys():
                    ids[el['beadId']] = {}
                if el['id'] not in ids[el['beadId']].keys():
                    ids[el['beadId']][el['id']] = {}
                ids[el['beadId']][el['id']][el['type']] = el['path']
            else:
                if el['beadId'] not in sharedFiles.keys():
                    sharedFiles[el['beadId']] = {}
                sharedFiles[el['beadId']][el['type']] = el['path']

        # append a reference to the shared file to each trial
        for idStr, el in ids.items():
            if idStr in sharedFiles.keys():
                for trial in el.values():
                    trial.update(sharedFiles[idStr])

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
        cols = self.readColumnTitles(self.header)
        units.update(cols['units'])

        # add id from header file name
        idDict = self.isDataFile(self.header)
        if idDict['id']:
            meta['id'] = idDict['id']
        else:
            meta['id'] = idDict['beadId']

        # add trap names
        meta['traps'] = meta.subDictKeys()

        return meta, units

    def getData(self):
        """
        Return the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        data = self.readToDataframe(self.data)
        return data

    def getDataSegment(self, tmin, tmax, chunkN=10000):
        """
        Returns the data between ``tmin`` and ``tmax`` by reading the datafile chunkwise until ``tmax`` is reached.

        Args:
            tmin (`float`): minimum data timestamp
            tmax (`float`): maximum data timestamp
            chunkN (`int`): number of rows to read per chunk

        Returns:
            :class:`pandas.DataFrame`
        """

        # read required information about file and create the chunked iterator
        cols = self.readColumnTitles(self.data)
        # read the first data line to allow conversion between absolute and relative time
        firstLine = pd.read_csv(self.data, sep='\t', skiprows=cols['n'], header=None,
                                names=cols['names'], nrows=1)
        t0 = firstLine.time.iloc[0]
        iterCsv = pd.read_csv(self.data, sep='\t', skiprows=cols['n']+1, header=None,
                              names=cols['names'], iterator=True, chunksize=chunkN, engine='c',
                              dtype=np.float64)

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

    @staticmethod
    def calculateForce(meta, units, data):
        """
        Calculate forces from Diff signal and calibration values.

        Args:
            meta (:class:`.MetaDict`): metadata
            units (:class:`.UnitDict`): unit metadata
            data (:class:`pandas.DataFrame`): data

        Returns:

            Updated versions of the input parameters

            * meta (:class:`.MetaDict`)
            * units (:class:`.UnitDict`)
            * data (:class:`pandas.DataFrame`)
        """

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

        return meta, units, data

    def postprocessData(self, meta, units, data):
        """
        Modify the time array to use relative times (but keep the absolute time) and calculate forces.

        Args:
            meta: :class:`tweezers.MetaDict`
            units: :class:`tweezers.UnitDict`
            data: :class:`pandas.DataFrame`

        Returns:
            Updated versions of the input parameters

            * meta (:class:`.MetaDict`)
            * units (:class:`.UnitDict`)
            * data (:class:`pandas.DataFrame`)
        """

        # create relative time column but keep absolute time
        data['absTime'] = data.time.copy()
        data.loc[:, 'time'] -= data.loc[0, 'time']
        units['absTime'] = 's'

        # calculate forces
        meta, units, data = self.calculateForce(meta, units, data)

        # calculate bead distance centre to centre, only meaningful for two trapped beads
        data['xDist'] = data.pmXBead - data.aodXBead
        data['yDist'] = data.pmYBead - data.aodYBead
        data['distance'] = np.sqrt((data.pmYBead - data.aodYBead)**2 + (data.pmXBead - data.aodXBead)**2)
        units['xDist'] = 'nm'
        units['yDist'] = 'nm'
        units['distance'] = 'nm'

        return meta, units, data

    def findHeaderLine(self, file):
        """
        Find the line number of the first header line, searches for ``### DATA ###``

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
            `dict` with keys `names` (`list`), `units` (:class:`.UnitDict`) and `n`
        """
        # read header line
        n = 0
        with file.open(encoding='utf-8') as f:
            for line in f:
                n += 1
                if line.startswith('#'):
                    # skip empty line
                    next(f)
                    headerLine = next(f)
                    n += 2
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

        return {'names': colHeaders, 'units': colUnits, 'n': n}

    def readToDataframe(self, file):
        """
        Read the given file into a :class:`pandas.DataFrame` and skip the header lines.

        Args:
            file (:class:`pathlib.Path`): path to file

        Returns:
            :class:`pandas.DataFrame`
        """

        cols = self.readColumnTitles(file)
        df = pd.read_csv(str(file), sep='\t', dtype=np.float64, skiprows=cols['n'], header=None,
                         names=cols['names'], engine='c')
        return df

    def getAnalysisFile(self):
        """
        Create the analysis file name.

        Returns:
            :class:`pathlib.Path`
        """

        filename = self.data.parent.joinpath(self.data.name.replace('DATA', 'ANALYSIS'))
        return filename
