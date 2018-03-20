from nptdms import TdmsFile
import re
import pandas as pd
from pathlib import Path
from collections import OrderedDict

from .BaseSource import BaseSource
import tweezers as t
from tweezers.ixo.decorators import lazy


class TdmsCTrapSource(BaseSource):
    """
    Data source for TDMS files from the Lumicks C-Trap.
    """

    # path to tdms file
    tdmsFile = None

    def __init__(self, data=None, analysis=None):
        """
        Args:
            data (`str` or :class:`pathlib.Path`): path to TDMS file

        Returns:
            :class:`.TdmsCTrapSource`
        """

        super().__init__()
        self.tdmsFile = Path(data)
        if analysis:
            self.analysis = Path(analysis)

    @lazy
    def tdms(self):
        """
        Creates the TDMS file object which automatically reads in the data.

        Returns:
            :class:`nptdms.TdmsFile`
        """

        return TdmsFile(str(self.tdmsFile))

    @staticmethod
    def isDataFile(path):
        """
        Checks if a given file is a valid data file and returns its ID and type

        Args:
            path (:class:`pathlib.Path`): file to check

        Returns:
            `dict` with ``id`` and ``type``
        """

        _path = Path(path)
        m = re.match('^(?P<beadId>[0-9\-]{15}.*#\d{3})(?P<trial>-\d{3})( (?P<type>[A-Z]+))?\.[a-zA-Z]{3,4}$',
                     _path.name)
        if m:
            ide = None
            if m.group('trial'):
                ide = '{}{}'.format(m.group('beadId'), m.group('trial'))
            tipe = m.group('type').lower()
            if not tipe:
                tipe = 'data'
            res = {'beadId': m.group('beadId'),
                   'id': ide,
                   'type': tipe,
                   'path': _path}
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
            `dict`
        """

        _path = Path(path)

        # get a list of all files and their properties
        files = TdmsCTrapSource.getAllFiles(_path)
        sources = OrderedDict()

        # sort files
        for el in files:
            if el['beadId'] not in sources.keys():
                sources[el['beadId']] = OrderedDict()
            if el['id'] not in sources[el['beadId']].keys():
                sources[el['beadId']][el['id']] = cls()
            # ToDo requries testing
            setattr(sources[el['beadId']][el['id']], el['type'], el['path'])

        return sources

    def getMetadata(self):
        """
        Return the metadata of the experiment.

        Returns:
            :class:`tweezers.MetaDict` and :class:`tweezers.UnitDict`
        """

        # hold metadata
        meta = t.MetaDict()
        units = t.UnitDict()

        # get metadata from groups
        groups = [self.tdms.object(), self.tdms.object('FD Data')]
        for group in groups:
            metaTmp, unitsTmp = self.convertProperties(group.properties)
            meta.update(metaTmp)
            units.update(unitsTmp)

        # get metadata from channels
        for channel in self.tdms.group_channels('FD Data'):
            ide = self.getKeyAndUnit(channel.channel)
            # store unit of channel using its property key to prevent clashes of nested channel information
            channelKey = self.getStandardPropertyId(ide['key'])
            if ide['unit']:
                units[channelKey] = ide['unit']
            metaTmp, unitsTmp = self.convertProperties(channel.properties, channel=ide['key'])
            meta.update(metaTmp)
            units.update(unitsTmp)

        return meta, units

    def getData(self):
        """
        Return the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        # create emtpy DataFrame
        data = pd.DataFrame()
        # get all channels from 'FD Data' group
        channels = self.tdms.group_channels('FD Data')
        # add all the channels to the DataFrame with appropriate column names
        for channel in channels:
            name = self.getKeyAndUnit(channel.channel)
            name = self.getStandardPropertyId(name['key'])
            data[name] = channel.data
        return data

    def getDataSegment(self, tmin, tmax, chunkN=10000):
        """
        Returns the data between ``tmin`` and ``tmax``. Unfortunately, the ``nptdms`` always reads in all the data
        when opening the file. So this basically just returns a subset of the already read data and does not speed up things.

        Args:
            tmin (float): minimum data timestamp
            tmax (float): maximum data timestamp
            chunkN (int): number of rows to read per chunk

        Returns:
            :class:`pandas.DataFrame`
        """

        data = self.getData()
        data = data.query('@tmin <= time <= @tmax').copy()
        return data

    def postprocessData(self, meta, units, data):
        """
        Convert time column in data from [ms] to [s].

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

        data['time'] /= 1000
        units['time'] = 's'

        return meta, units, data

    def setMeta(self, meta, keyList, value):
        """
        Set an item in a dictionary (e.g. :class:`tweezers.MetaDict`) based on a list of keys that describe the path
        to the value.

        Args:
            meta (`dict`): dictionary to update, in this context it will be :class:`tweezers.MetaDict` or
                         :class:`tweezers.UnitDict`
            keyList (`list`): list of keys
            value: the value to store
        """

        path = {keyList[-1]: value}

        # if there are keys left, we need to build a nested structure
        for key in reversed(keyList[:-1]):
            path = {key: path}

        meta.update(path)

    def convertProperties(self, properties, channel=None):
        """
        Convert a `dict` of TDMS properties to :class:`.MetaDict` and :class:`.UnitDict`. Keys will be replaced by
        standardized identifiers.

        Args:
            properties (`dict`): dictionary of TDMS properties
            channel (`str`): if the properties belong to a channel, pass its name as a parameter here for proper
                             choice of standard identifiers

        Returns:
            * meta (:class:`.MetaDict`)
            * units (:class:`.UnitDict`)
        """

        meta = t.MetaDict()
        units = t.UnitDict()

        for key, value in properties.items():
            # skip specific property
            if key == 'NI_ArrayColumn':
                continue
            # get identifier and unit
            idOrig = self.getKeyAndUnit(key)
            # get matching standard identifier
            if channel:
                # get nested channel id for channel name and property id for property
                idStd = [self.getStandardChannelId(channel),
                         self.getStandardPropertyId(idOrig['key'])]
            else:
                # get only property id
                idStd = [self.getStandardPropertyId(idOrig['key'])]
            self.setMeta(meta, idStd, value)
            # add unit if available
            if idOrig['unit']:
                self.setMeta(units, idStd, idOrig['unit'])

        return meta, units

    def getKeyAndUnit(self, key):
        """
        Extract key (name) and, if available, its unit from a string.

        Args:
            key (`str`): string to search for key and unit

        Returns:
            `dict` with keys: ``key`` and ``unit``
        """

        regex = re.compile('^(?P<key>.*?)(?:\s?\((?P<unit>\D+)\))?$')
        res = regex.search(key)
        return res.groupdict()

    @staticmethod
    def getStandardPropertyId(key):
        """
        Get a unique ID for a given property and column name for a channel's data.

        Args:
            key (`str`): the key to look up

        Returns:
            `str`
        """

        # reduce number of variations: strip spaces
        # one could also change everything to lower case but that would decrease readability
        key = key.strip()

        keyMapper = {
            # channel stuff
            'Force Channel 0': 'chan0Force',
            'Force Channel 1': 'chan1Force',
            'Force Channel 2': 'chan2Force',
            'Force Channel 3': 'chan3Force',
            'Distance 1': 'dist1',
            'Distance 2': 'dist2',
            'Force Channel 0 STDEV': 'chan0ForceStd',
            'Force Channel 1 STDEV': 'chan1ForceStd',
            'Force Channel 2 STDEV': 'chan2ForceStd',
            'Force Channel 3 STDEV': 'chan3ForceStd',
            'Force Trap 0': 't0Force',
            'Force Trap 1': 't1Force',
            'Force Trap 0 STDEV': 't0ForceStd',
            'Force Trap 1 STDEV': 't1ForceStd',
            'Bead 1 X position': 'bead1X',
            'Bead 2 X position': 'bead2X',
            'Bead 3 X position': 'bead3X',
            'Bead 4 X position': 'bead4X',
            'Bead 1 Y position': 'bead1Y',
            'Bead 2 Y position': 'bead2Y',
            'Bead 3 Y position': 'bead3Y',
            'Bead 4 Y position': 'bead4Y',

            # general stuff
            'Molecule #': 'molecule',
            'File #': 'file'
        }

        if key in keyMapper.keys():
            res = keyMapper[key]
        else:
            # camelCase the key
            res = TdmsCTrapSource.toCamelCase(key)
        return res

    @staticmethod
    def getStandardChannelId(key):
        """
        Get a standardized name for a channel which will be used to store nested metadata. The data of the channel
        will be stored using the result of :meth:`.getStandardPropertyId` as column name and key for the ``units``
        dictionary.

        Args:
            key (`str`): the key to look up

        Returns:
            `str`
        """

        # reduce number of variations: strip spaces
        # one could also change everything to lower case but that would decrease readability
        key = key.strip()

        keyMapper = {
            'Force Channel 0': 'chan0',
            'Force Channel 1': 'chan1',
            'Force Channel 2': 'chan2',
            'Force Channel 3': 'chan3',
        }

        if key in keyMapper.keys():
            res = keyMapper[key]
        else:
            # camelCase the key
            res = TdmsCTrapSource.toCamelCase(key)
        return res

    @staticmethod
    def toCamelCase(string):
        """
        Convert a `str` to ``camelCase``.
        Args:
            string (`str`): string to convert

        Returns:
            `str`
        """

        string = ''.join(x for x in string.title() if not x.isspace())
        string = string[0].lower() + string[1:]
        return string

    def getAnalysisFile(self):
        """
        Create the analysis file name.

        Returns:
            :class:`pathlib.Path`
        """

        filename = self.data.with_name('{} ANALYSIS{}'.format(self.data.stem, self.data.suffix))
        return filename
