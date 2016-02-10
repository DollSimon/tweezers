from pathlib import Path
import json
from collections import OrderedDict
import pandas as pd
import numpy as np
import re

from .BaseSource import BaseSource
import tweezers as t


class TxtBiotecSource(BaseSource):
    """
    Data source for *.txt files from the Biotec tweezers.
    """

    # hold paths to respective files
    header = None
    psd = None
    data = None
    ts = None
    # path to data, not correct if files sit in different folders
    path = None

    def __init__(self, data=None, psd=None, ts=None):
        """
        Constructor for TxtBiotecSource

        Args:
            data (:class:`pathlib.Path`): path to data file to read, if the input is of a different type, it is given to
                                           :class:`pathlib.Path` to try to create an instance
            psd (:class:`pathlib.Path`): path to psd file to read, similar to `data` input
        """

        super().__init__()

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

        self.path = self.header.parent

    @classmethod
    def fromDirectory(cls, path):
        """
        Creates a data source from a given folder that should contain the data files (PSD, TS, data).

        Args:
            path (:class:`pathlib.Path`): path to the data folder

        Returns:
            :class:`tweezers.io.TxtBiotecSource`
        """

        pPath = Path(path)
        if not pPath.exists() and pPath.is_dir():
            raise ValueError('Invalid path given')

        files = {'psd': ' PSD.txt', 'ts': ' TS.txt', 'data': '.txt'}
        kwargs = {}
        for key, value in files.items():
            file = pPath / Path(pPath.name + value)
            if file.exists() and cls.isDataFile(file):
                kwargs[key] = file

        if not kwargs:
            raise ValueError('No files found at given path')

        return cls(**kwargs)

    @staticmethod
    def isDataFile(path):
        """
        Checks if a given file is a valid data file.

        Args:
            path:

        Returns:
            bool
        """

        pPath = Path(path)
        if re.search('\d{4}(?:_\d{2}){5}.*\.txt', pPath.name):
            return True
        else:
            return False

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
        return ts

    def getData(self):
        """
        Return the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        data = self.readToDataframe(self.data)
        return data

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
        df = pd.read_csv(str(file), sep='\t', dtype=np.float64,
                         skiprows=nHeaderLine+1, header=None, names=colHeaders)
        return df
