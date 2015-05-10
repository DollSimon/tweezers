from pathlib import Path
import json
from collections import OrderedDict
import pandas as pd
import numpy as np

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
            ts = self.makePath(ts)
            self.ts = ts
            self.header = ts

        if psd:
            psd = self.makePath(psd)
            self.psd = psd
            self.header = psd

        if data:
            data = self.makePath(data)
            self.data = data
            self.header = data

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

        return meta, units

    def getPsd(self):
        """
        Returns the power spectral density (PSD) used for the calibration of the experiment by the data source.

        Returns:
            :class:`pandas.DataFrame`
        """

        psd = self.readToDataframe(self.psd)
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

    def makePath(self, path):
        """
        Convert input to :class:`pathlib.Path`.

        Args:
            path (str): path to be converted

        Returns:
            :class:`pathlib.Path`: path object
        """

        if not isinstance(path, Path):
            path = Path(path)

        return path

    def findHeaderLine(self, file):
        """
        Find the line number of the first header line, searches for '### DATA ###'


        Args:
            :class:`pathlib.Path`: path to file
        """

        n = 0
        with file.open(encoding='utf-8') as f:
            for line in f:
                if line.startswith('#'):
                    break
                else:
                    n += 1

        return n + 2

    def readToDataframe(self, file):
        """
        Read the given file into a :class:`pandas.DataFrame` and skip the header lines.

        Args:
            :class:`pathlib.Path`: path to file

        Returns:
            :class:`pandas.DataFrame`
        """

        nHeaderLine = self.findHeaderLine(file)
        df = pd.read_csv(str(file), skiprows=nHeaderLine, sep='\t', dtype=np.float64)
        return df