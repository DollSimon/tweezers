import numpy as np
import pandas as pd
from pathlib import Path
import re
from collections import OrderedDict
from lumicks import pylake

from tweezers.ixo.collections import IndexedOrderedDict
from .BaseSource import BaseSource
from tweezers.meta import MetaDict, UnitDict

class Hdf5CTrapSource(BaseSource):
    dataPath = None
    data = None

    def __init__(self, data=None):
        self.dataPath = data
        self.data = pylake.File(self.dataPath)

    def __deepcopy__(self, memodict={}):
        return self.__class__(self.dataPath)

    def getData(self):
        return pd.DataFrame()

    def getAllData(self):
        data = IndexedOrderedDict()
        for groupName in self.data.h5.keys():
            if groupName == 'Calibration':
                continue

            for channelName in self.data[groupName].h5.keys():
                channel = self.data[groupName][channelName]
                dataColumns = {'t': channel.timestamps, 'd': channel.data}
                key = self.getShortName(f'{groupName}/{channelName}')
                data[key] = pd.DataFrame(dataColumns)
        return data

    @staticmethod
    def getShortName(name):
        names = {
            'Bead position': 'beads',
            'Bead position/Bead 1 X': 'bead1x',
            'Bead position/Bead 1 Y': 'bead1y',
            'Bead position/Bead 2 X': 'bead2x',
            'Bead position/Bead 2 Y': 'bead2y',
            'Bead 1 X': 'bead1x',
            'Bead 1 Y': 'bead1y',
            'Bead 2 X': 'bead2x',
            'Bead 2 Y': 'bead2y',
            'Force HF': 'force',
            'Force HF/Force 1x': 'force1x',
            'Force HF/Force 1y': 'force1y',
            'Force HF/Force 2x': 'force2x',
            'Force HF/Force 2y': 'force2y',
            'Trap position': 'trapPos',
            'Trap position/1X': 'trapPos1x',
            'Trap position/1Y': 'trapPos1y',
            'Force 1x': 'trap1x',
            'Force 1y': 'trap1y',
            'Force 2x': 'trap2x',
            'Force 2y': 'trap2y',
            '1X': 'trap1x',
            '1Y': 'trap1y'
        }

        return names[name]

    def getMetadata(self):
        meta = MetaDict()
        units = UnitDict()

        # build list of available traps
        meta['traps'] = []

        # get force calibration and trap names
        for force in ['force1x', 'force1y', 'force2x', 'force2y', 'force3x', 'force3y', 'force4x', 'force4y']:
            try:
                calib = getattr(self.data, force).calibration[0]
            except IndexError:
                continue

            # create trap name from
            trapName = 'trap' + force[5:]
            meta['traps'].append(trapName)
            meta[trapName] = MetaDict(calib)
            units[trapName] = UnitDict()

        # check for sampling rate for PSD
        try:
            meta['psdSamplingRate'] = meta[meta.traps[0]]['Sample rate (Hz)']
        except IndexError:
            pass

        # put some other defaults
        meta['psdType'] = 'normal'

        # convert some metadata in units and / or keys
        refTrap = meta.traps[0]
        # get viscosity and convert from Pa s to pN s / nm^2
        meta['viscosity'] = meta[refTrap]['Viscosity (Pa*s)'] * 1E-6
        units['viscosity'] = 'pN s / nm^2'
        meta['temperature'] = meta[refTrap]['Temperature (C)']
        units['temperature'] = 'C'

        for trap in meta.traps:
            meta[trap]['beadDiameter'] = meta[trap]['Bead diameter (um)']
            units[trap]['beadDiameter'] = 'um'

        meta['beadId'] = self.dataPath.name[:-3]

        return meta, units

    def getSingleDataFrame(self, group='Force HF'):
        # get all channel names from the group
        keys = list(self.data.h5[group].keys())
        # get get timestamps
        data = {'absT': self.data[group][keys[0]].timestamps}
        # get data for each channel as array
        for key in keys:
            channel = self.data[group][key]
            # check if timestamps are the same
            if not np.array_equal(channel.timestamps[:3], data['absT'][:3]):
                raise ValueError(f'Timestamps in "{group}" are not consistent.')
            # store data
            data[self.getShortName(key)] = channel.data

        # get length to crop each column to
        sizes = np.array([column.shape[0] for column in data.values()])
        maxLen = sizes.min()
        for key, column in data.items():
            data[key] = column[:maxLen]

        # add time column in seconds
        data['t'] = (data['absT'] - data['absT'][0]) / 1e9
        # convert to DataFrame
        data = pd.DataFrame(data)

        return data

    def getForceDf(self):
        return self.getSingleDataFrame(group='Force HF')

    def getTrapDf(self):
        return self.getSingleDataFrame(group='Trap position')

    def getBeadDf(self):
        return self.getSingleDataFrame(group='Bead position')

    @staticmethod
    def forceToVolt(force, calibration):
        forceSens = calibration['Response (pN/V)']
        offset = calibration['Offset (pN)']
        volt = (force - offset) / forceSens
        return volt

    @staticmethod
    def calculateForce(meta, units, data):
        return meta, units, data

    @staticmethod
    def isDataFile(path):
        """
        Checks if a given file is a valid data file and returns its ID and type.

        Args:
            path (:class:`pathlib.Path`): file to check

        Returns:
            `dict` with ``id`` and ``type``
        """

        _path = Path(path)
        m = re.match('^(?P<beadId>[0-9]{8}\-[0-9]{6}.*)\.h5$',
                     _path.name)
        if m:
            res = {'beadId': m.group('beadId'),
                   'id': m.group('beadId'),
                   'path': _path}
            return res
        else:
            return False

    @classmethod
    def getAllSources(cls, path):
        """
        Get a list of all IDs and their data sources that are at the given path and its subfolders.

        Args:
            path (:class:`pathlib.Path`): root path for searching

        Returns:
            `dict`
        """

        _path = Path(path)

        # get a list of all files and their properties
        files = cls.getAllFiles(_path)
        sources = OrderedDict()

        for el in files:
            sources[el['id']] = cls(el['path'])
        return sources
