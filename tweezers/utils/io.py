from tweezers.io import TxtBiotecSource
from tweezers import TweezersData


def loadIds(ids, cls=TxtBiotecSource):
    """
    Load all data names (IDs) given in the input list.
    Args:
        ids (dict): :class:`dict` with ID strings as keys and :class:`dict` as values. The value is passed on to the
        `fromId` method of the data source class provided in `cls`.

        cls (class): Type of the data source to use. By default this is
        :class:`tweezers.io.TxtBiotecSource.TxtBiotecSource`.

    Returns:
        :class:`list` of :class:`tweezers.TweezersData`
    """

    # get sorted list of ids
    idKeys = list(ids.keys())
    idKeys.sort()

    # create data objects
    data = []
    for idStr in idKeys:
        try:
            td = TweezersData(cls.fromIdDict(ids[idStr]))
            data.append(td)
        except ValueError:
            # we might want to put a more descriptive message here
            print('Error loading data set: "' + idStr + '"')

    return data


def getAllIds(path, cls=TxtBiotecSource):
    """
    Get a list of all IDs from the static method of the given DataSource class.

    Args:
        path (:class:`pathlib.Path`): root path of the data structure
        cls: class that implements the `getAllIds` method

    Returns:
        :class:`dir`
    """

    return cls.getAllIds(path)


def getIdsByName(name, path, cls=TxtBiotecSource):
    """
    Get all IDs from the data structure in the given path whose ID end on the given name string.
    Args:
        name (str or list): name of the experiment, last section of the ID
        path (:class:`pathlib.Path`): root path to the data structure

    Returns:
        :class:`dir`
    """

    # get all IDs
    ids = getAllIds(path, cls=cls)

    # filter by given name
    resIds = {key: value for key, value in ids.items() if key.endswith(name)}
    return resIds


def getIds(names, path, cls=TxtBiotecSource):
    """

    Args:
        names:
        path:
        cls:

    Returns:

    """

    # check if names is a string and convert to list
    if isinstance(names, str):
        names = [names]

    ids = getAllIds(path, cls=cls)

    # filter by names
    resIds = {}
    for name in names:
        tmpIds = {key: value for key, value in ids.items() if (key.endswith(name) or key.startswith(name))}
        resIds.update(tmpIds)

    return resIds