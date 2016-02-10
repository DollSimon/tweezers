from tweezers.io import TxtBiotecSource
from tweezers import TweezersData


def loadIds(path, ids, cls=TxtBiotecSource):
    """
    Load all data names (IDs) given in the input list.
    Args:
        path (:pathlib:`Path`): path to the data root folder
        ids (:class:`list`): list of names

    Returns:
        :class:`list` of :class:`tweezers.TweezersData`
    """

    data = []
    for idStr in ids:
        try:
            td = TweezersData(cls.fromId(path, idStr))
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
        :class:`list` of :class:`str`
    """

    return cls.getAllIds(path)


def getIdsByName(path, name, cls=TxtBiotecSource):
    """
    Get all IDs from the data structure in the given path whose ID end on the given name string.
    Args:
        path (:class:`pathlib.Path`): root path to the data structure
        name (str): name of the experiment, last section of the ID

    Returns:
        :class:`list` of :class:`str`
    """

    # get all IDs
    ids = getAllIds(path, cls=cls)

    # filter by given name
    resIds = [x for x in ids if x.endswith(name)]
    return resIds
