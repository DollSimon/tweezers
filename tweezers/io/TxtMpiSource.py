from pathlib import Path
import json
import re
import numpy as np
import os
from collections import OrderedDict

from .TxtMpiFile import TxtMpiFile
from .BaseSource import BaseSource
from tweezers.meta import MetaDict, UnitDict


class TxtMpiSource(BaseSource):
    """
    Data source for \*.txt files from the MPI with the old style header or the new JSON format.
    """

    data = None
    psd = None
    ts = None

    def __init__(self, data=None, psd=None, ts=None):
        """
        Args:
            path (:class:`patlhlib.Path`): path to file to read, if the input is of a different type, it is given to
                                           :class:`pathlibh.Path` to try to create an instance
        """

        super().__init__()

        # go through input
        if data:
            self.data = TxtMpiFile(data)
        if psd:
            self.psd = TxtMpiFile(psd)
        if ts:
            self.ts = TxtMpiFile(ts)

    @staticmethod
    def isDataFile(path):
        """
        Checks if a given file is a valid data file and returns its ID and type.

        Args:
            path (:class:`pathlib.Path`): file to check

        Returns:
            :class:`dict` with `id` and `type`
        """

        pPath = Path(path)
        m = re.match('^((?P<type>[A-Z]+)_)?(?P<id>(?P<trial>[0-9]{1,3})_Date_[0-9_]{19})\.txt$',
                     pPath.name)
        if m:
            tipe = 'data'
            if m.group('type'):
                tipe = m.group('type').lower()
            res = {'id': m.group('id'),
                   'trial': m.group('trial'),
                   'type': tipe,
                   'path': pPath}
            return res
        else:
            return False

    @classmethod
    def getAllSources(cls, path):
        """
        Get a list of all IDs and their files that are at the given path and its subfolders.

        Args:
            path (:class:`pathlib.Path`): root path for searching

        Returns:
            `dir`
        """

        _path = Path(path)

        # get a list of all files and their properties
        files = cls.getAllFiles(_path)
        sources = OrderedDict()

        # sort files that belong to the same id
        for el in files:
            if el['id'] not in sources.keys():
                sources[el['id']] = cls()
            setattr(sources[el['id']], el['type'], TxtMpiFile(el['path']))

        return sources

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
            metaTmp, unitsTmp = self.ts.getMetadata()

            # make sure we don't override important stuff that by accident has the same name
            self.renameKey('nSamples', 'psdNSamples', meta=metaTmp, units=unitsTmp)
            self.renameKey('dt', 'psdDt', meta=metaTmp, units=unitsTmp)

            # set time series unit
            unitsTmp['timeseries'] = 'V'

            # update the dictionaries with newly found values
            meta.update(metaTmp)
            units.update(unitsTmp)

        if self.psd:
            metaTmp, unitsTmp = self.psd.getMetadata()

            # make sure we don't override important stuff that by accident has the same name
            # also, 'nSamples' and 'samplingRate' in reality refer to the underlying timeseries data
            self.renameKey('nSamples', 'psdNSamples', meta=metaTmp, units=unitsTmp)
            self.renameKey('dt', 'psdDt', meta=metaTmp, units=unitsTmp)

            # set psd unit
            unitsTmp['psd'] = 'V^2 / Hz'

            meta.update(metaTmp)
            units.update(unitsTmp)

        if self.data:
            metaTmp, unitsTmp = self.data.getMetadata()

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

        # make sure all axes have the beadDiameter
        meta['pmY']['beadDiameter'] = meta['pmX']['beadDiameter']
        units['pmY']['beadDiameter'] = units['pmX']['beadDiameter']
        meta['aodY']['beadDiameter'] = meta['aodX']['beadDiameter']
        units['aodY']['beadDiameter'] = units['aodX']['beadDiameter']

        # add trap names
        meta['traps'] = meta.subDictKeys()

        return meta, units

    def getData(self):
        """
        Return the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.data:
            raise ValueError('No data file given.')

        return self.data.getData()

    def getDataSegment(self, tmin, tmax, chunkN=10000):
        """
        Returns the data between ``tmin`` and ``tmax``.

        Args:
            tmin (float): minimum data timestamp
            tmax (float): maximum data timestamp
            chunkN (int): number of rows to read per chunk

        Returns:
            :class:`pandas.DataFrame`
        """

        meta, units = self.getMetadata()
        nstart = int(meta.samplingRate * tmin)
        nrows = int(meta.samplingRate * (tmax - tmin))
        return self.data.getDataSegment(nstart, nrows)

    def getPsd(self):
        """
        Return the PSD of the thermal calibration of the experiment as computed by LabView.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.psd:
            raise ValueError('No PSD file given.')

        # read psd file which also contains the fitting
        data = self.psd.getData()
        # ignore the fitting
        titles = [title for title, column in data.iteritems() if not title.endswith('Fit')]
        return data[titles]

    def getPsdFit(self):
        """
        Return the LabView fit of the Lorentzian to the PSD.

        Returns:
            :class:`pandas.DataFrame`
        """

        if not self.psd:
            raise ValueError('No PSD file given.')

        # the fit is in the psd file
        data = self.psd.getData()
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

        data = self.ts.getData()
        # remove "Diff" from column headers
        columnHeader = [title.split('Diff')[0] for title in data.columns]
        data.columns = columnHeader
        return data

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
            data[trap + 'Force'] = (data[trap + 'Diff'] - m['zeroOffset']) \
                                   / m['displacementSensitivity'] \
                                   * m['stiffness']
            units[trap + 'Force'] = 'pN'

        # invert PM force, is not as expected in the raw data
        # data.pmYForce = -data.pmYForce

        # calculate mean force per axis, only meaningful for two traps
        data['xForce'] = (data.pmXForce + data.aodXForce) / 2
        data['yForce'] = (data.pmYForce - data.aodYForce) / 2

        units['xForce'] = 'pN'
        units['yForce'] = 'pN'

        return meta, units, data

    def postprocessData(self, meta, units, data):
        """
        Create time array, calculate forces etc.

        Args:
            meta (:class:`tweezers.MetaDict`): meta dictionary
            units (:class:`tweezers.UnitDict`): units dictionary
            data (:class:`pandas.DataFrame`): data

        Returns:
            Updated versions of the input parameters

            * meta (:class:`.MetaDict`)
            * units (:class:`.UnitDict`)
            * data (:class:`pandas.DataFrame`)
        """

        data['time'] = np.arange(0, meta['dt'] * len(data), meta['dt'])
        units['time'] = 's'

        meta, units, data = self.calculateForce(meta, units, data)

        data['distance'] = np.sqrt(data.xDist**2 + data.yDist**2)
        units['distance'] = 'nm'

        return meta, units, data

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

        meta = MetaDict()
        units = UnitDict()

        # meta[self.getStandardIdentifier('tsSamplingRate')] = 80000
        #
        # units[self.getStandardIdentifier('tsSamplingRate')] = 'Hz'

        return meta, units

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
