import logging as log
import collections

from tweezers.io import TxtBiotecSource
from tweezers import TweezersData
from tweezers import TweezersCollection
from tweezers.ixo.collections import isNestedDict


def loadId(idDict, cls=TxtBiotecSource):
    """
    Create :class:`tweezers.TweezersData` instance from given ID-`dict` using the specified data source.

    Args:
        idDict (`dict`): ID dictionary
        cls (:class:`tweezers.io.BaseSource`): data source class

    Returns:
        Child of :class:`tweezers.io.BaseSource`
    """

    return TweezersData(cls.fromIdDict(idDict))

def loadIds(ids, cls=TxtBiotecSource):
    """
    Load all IDs given in the input list.

    Args:
        ids (`dict`): `dict` with ID strings as keys and `dict` as values. The value is passed on to the
            ``fromId`` method of the data source class provided in ``cls``. Also works for nested dictionaries.

        cls: Type of the data source to use. By default this is :class:`tweezers.io.TxtBiotecSource`.

    Returns:
        `list` of :class:`tweezers.TweezersData`
    """

    # get sorted list of ids
    idKeys = list(ids.keys())
    idKeys.sort()

    # create data objects
    data = TweezersCollection()
    for idStr in idKeys:
        if isNestedDict(ids[idStr]):
            data[idStr] = loadIds(ids[idStr])
        else:
            try:
                td = TweezersData(cls.fromIdDict(ids[idStr]))
                data[idStr] = td
            except ValueError:
                # we might want to put a more descriptive message here
                print('Error loading data set: "' + idStr + '"')

    return data


def getAllIds(path, cls=TxtBiotecSource):
    """
    Get a list of all IDs from the static method of the given DataSource class.

    Args:
        path (:class:`pathlib.Path`): root path of the data structure
        cls: class that implements the ``getAllIds`` method

    Returns:
        `dir`
    """

    return cls.getAllIds(path)


def loadSegments(tc):
    """
    Load all segments from the given :class:`tweezers.TweezersCollection`.
    Args:
        tc (:class:`tweezers.TweezersCollection`): collection to read segements from

    Returns:
        :class:`tweezers.TweezersCollection`
    """

    data = TweezersCollection()
    for id, t in tc.items():
        if isinstance(t, TweezersCollection):
            data[id] = loadSegments(t)
        else:
            if not t.segments:
                log.warning('No segments defined in dataset "{}"'.format(t.meta['id']))
            for segmentId in t.segments:
                ts = t.getSegment(segmentId)
                data[ts.meta['id']] = ts
    return data
