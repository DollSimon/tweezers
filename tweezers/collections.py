import re
import pandas as pd
import datetime
from pathlib import Path
from datetime import datetime

from tweezers.ixo.collections import IndexedOrderedDict
from tweezers.container.TweezersAnalysis import TweezersAnalysis
from tweezers.io.TxtBiotecSource import TxtBiotecSource
from tweezers.io.BaseSource import BaseSource
from tweezers import TweezersData


class TweezersCollection(IndexedOrderedDict):
    """
    Collection of :class:`.TweezersData`. Inherits from
    :class:`.IndexedOrderedDict` with keys being ID names.
    """

    def flatten(self):
        """
        Flatten a data collection, i.e. remove nested collections. Returns a copy of the collection.

        Returns:
            :class:`.TweezersCollection`
        """

        res = self.__class__()

        for key in self.keys():
            if isinstance(self[key], TweezersCollection):
                # if the item is a collection itself, append its flattened result
                res.update(self[key].flatten())
            else:
                # append the item directly
                res[key] = self[key]

        return res.sorted()

    def filter(self, filterExp):
        """
        Filter keys based on whether they match a regular filter expression or not.

        Args:
            filterExp (`str`): regular expression to filter keys

        Returns:
            :class:`.TweezersCollection`

        Example:
            ::

                 path = '/Volumes/grill/Tweezers/Data/Raw/data'
                 ids = getAllIds(path)
                 fids = ids.filter('2017-03.*Hyd')
        """

        # string based filter for keys
        res = self.__class__()
        for key in self.keys():
            if re.search(filterExp, key):
                res[key] = self[key]

        return res


class TweezersDataCollection(TweezersCollection):
    """
    A class to hold multiple :class:`.TweezersData` references. It provides some convenience functions to handle these.
    """

    @classmethod
    def load(cls, path, source=TxtBiotecSource):
        """
        Load data from disk. This will recursively find all files in the provied `path` that can be used with the
        provided tweezers data source, construct a :class:`.TweezersData` from it and populate a
        :class:`.TwezersDataCollection` from all the found objects.

        This is probably the easiest way to load many data files.

        Args:
            path (`str` or :class:`pathlib.Path`): path to recursively search for data files that will be loaded as
            :class:`.TweezersData` objects
            source (:class:`tweezers.io.BaseSource.BaseSource`, optional): a tweezers data source used to
            identify valid data files and build the :class:`.TweezersData` object, defaults to
            :class:`tweezers.io.TxtBiotecSource`

        Returns:
            :class:`.TweezersDataCollection`
        """

        # get all data sources
        sources = source.getAllSources(path)

        # convert data sources to TweezersData
        res = cls._sourcesToData(sources)

        return res

    @classmethod
    def _sourcesToData(cls, sources):
        """
        Convert the found data sources to :class:`.TweezersData` objects
        Args:
            sources (dict): dictionary of datasources

        Returns:
            :class:`.TweezersDataCollection`
        """

        res = cls()
        for key, value in sources.items():
            if isinstance(value, BaseSource):
                res[key] = TweezersData(source=value)
            else:
                res[key] = cls._sourcesToData(value)
        return res

    def getAnalysis(self, path, groupByBead=True, onlySegments=False):
        """
        Convert all the :class:`.TweezersData` objects, held by this collection, to :class:`.TweezersAnalysis`
        objects.

        The option `groupByBead` will try to identify individual datasets (from individual source files) that belong
        to the same bead ID and create only one analysis object for each bead. All data belonging to this bead is
        collected in that one analysis object.
        If no `beadID` key is present in the metadata, an exception is raised.

        If the contained :class:`.TweezersData` object has segments, only the segments will be exported. Otherwise,
        the whole dataset is appended to the analysis object.

        Args:
            path (`str` or :class:`pathlib.Path`): export path for the :class:`.TweezersAnalysis` objects
            groupByBead (bool): group data by bead ID
            onlySegments (bool): if `True` only gets segments and skips files without any defined segments,
                                 otherwise these contain the whole datafile

        Returns:
            :class:`.TweezersAnalysisCollection`
        """
        res = TweezersAnalysisCollection()

        if groupByBead:
            # create one analysis file per bead, collect all the trial segments
            tcTmp = self.flatten()
            for t in tcTmp.values():
                # skip if there are not segments and we only export segments
                if onlySegments and not t.segments:
                    continue
                try:
                    beadId = t.meta.beadId
                except KeyError:
                    raise ValueError('TweezersDataCollection:getAnalysis: Grouping by bead not possible, no "beadId" present')
                if beadId not in res.keys():
                    # create new bead in collection
                    res[beadId] = TweezersAnalysis(path=path, name=beadId)
                    res[beadId].meta = t.meta
                    res[beadId].units = t.units
                    res[beadId].addField('segments')

                a = t.getAnalysis(path)
                for key, value in a.items():
                    if key in ['meta', 'units']:
                        # meta and units are added for all trials in the beginning so skip these fields
                        continue
                    if key in res[beadId].segments.keys():
                        # if the segment name already exists, throw an exception
                        # since we don't have a good way to create a unique segment id for all data sources,
                        # this is a reasonable fix, could be improved in the future
                        raise KeyError('TweezersDataCollection:getAnalysis: Bead ID "{}" already has a segment "{}"'.format(beadId, key))
                    res[beadId].segments[key] = value
        else:
            # just go through the structure recursively
            for key in self.keys():
                if isinstance(self[key], TweezersData):
                    # self[key] is a TwezersData object
                    res[key] = self[key].getAnalysis(path=path)
                else:
                    # self[key] is a nested TweezersDataCollection
                    res[key] = self[key].getAnalysis(path=path, groupByBead=groupByBead)

        return res.sorted()

    def filterByDate(self, date, method='newer', endDate=None):
        """
        Filter the `TweezersCollection` by date. Available methods are `newer`, `older` and `between`.
        For `between`, dates between `date` and `endDate` will be filtered.

        Args:
            date (`datetime.datetime` or str): reference date, if `str`, it should be in format "YYYY-MM-DD"
            method (`str`): one of `newer`, `older`, `between`
            endDate(`datetime.datetime): required if `type = 'between'`

        Returns:
            `tweezers.TweezersCollection`
        """

        if isinstance(date, str):
            try:
                date = datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                raise ValueError('filterByDate: `date` could not be converted to a `datetime.datetime object. Use '
                                 '"YYYY-MM-DD" notation')
        if not isinstance(date, datetime):
            raise ValueError('filterByDate: `date` is not a `datetime.datetime` object')
        if method is 'between':
            if isinstance(endDate, str):
                try:
                    endDate = datetime.strptime(endDate, '%Y-%m-%d')
                except ValueError:
                    raise ValueError('filterByDate: `endDate` could not be converted to a `datetime.datetime object. '
                                     'Use "YYYY-MM-DD" notation')
                if not isinstance(endDate, datetime):
                    raise ValueError('filterByDate: `endDate` is not a `datetime.datetime` object')

        res = self.__class__()
        for key, item in self.items():
            # start recursion
            if isinstance(item, TweezersCollection):
                tmp = item.filterByDate(date, method=method, endDate=endDate)
                # only add if there is a filtering result
                if tmp:
                    res[key] = item.filterByDate(date, method=method, endDate=endDate)
                continue

            # or work on current item
            time = item.source.getTime()
            if method is 'newer' and time >= date:
                res[key] = item
            elif method is 'older' and time <= date:
                res[key] = item
            elif method is 'between' and date <= time <= endDate:
                res[key] = item
        return res

    def getMetaFacets(self):
        """
        Create a :class:`pandas.DataFrame` facet view of the metadata of all datasets. This calls
        :meth:`tweezers.meta.MetaBaseDict.getFacets`.

        Returns:
            :class:`pandas.DataFrame`
        """

        res = []
        for item in self.values():
            if isinstance(item, TweezersCollection):
                res.append(item.getMetaFacets())
            else:
                res.append(item.meta.getFacets())

        return pd.concat(res, ignore_index=True, sort=False)


class TweezersAnalysisCollection(TweezersCollection):
    """
    A class to hold multiple :class:`.TweezersAnalysis` references. It provides some convenience functions to handle
    these.
    """

    @classmethod
    def load(cls, path):
        """
        Load data from disk. This will recursively find all analysis files in the provied `path` and load each of
        them into a :class:`.TweezersAnalysis`.

        This is probably the easiest way to load many analysis files.

        Args:
            path (`str` or :class:`pathlib.Path`): path to recursively search for analysis files

        Returns:
            :class:`.TweezersAnalysisCollection`
        """

        res = cls()

        _path = Path(path)
        for item in _path.iterdir():
            if item.is_dir():
                # recursively enter directory
                content = cls.load(item)
                # if it is not empty, append content
                if content:
                    res[item.name] = content
            if TweezersAnalysis.isAnalysisFile(item):
                res[item.name] = TweezersAnalysis.load(item)

        return res

    def save(self):
        """
        Saves all the :class:`.TweezersAnalysis` objects in this collection by calling :meth:`.TweezersAnalysis.save`.
        """

        # this will work recursively since save is a method in TweezersAnalysis and TweezersAnalysisCollection
        for value in self.values():
            value.save()
