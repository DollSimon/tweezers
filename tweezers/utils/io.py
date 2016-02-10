from pathlib import Path

from tweezers.io import TxtBiotecSource
from tweezers import TweezersData


def loadDirectories(directories, cls=TxtBiotecSource):
    """
    Load all directories given in the input list.
    Args:
        dirs (:class:`list`): list of directories

    Returns:
        :class:`list` of :class:`tweezers.TweezersData`
    """

    data = []
    for directory in directories:
        try:
            td = TweezersData(cls.fromDirectory(directory))
            data.append(td)
        except ValueError:
            pass

    return data


def getDirsById(path, id):
    """
    Get all directories in the given path whose name end on the given ID string.
    Args:
        path (:pathlib:`Path`): path to check for subdirectories
        id (str): id to search for

    Returns:
        :class:`list` of :pathlib:`Path`
    """

    # get all subdirectories
    dirs = [x for x in Path(path).iterdir() if x.is_dir()]

    # filter by ID
    resDirs = [x for x in dirs if x.name.endswith(id)]
    return resDirs