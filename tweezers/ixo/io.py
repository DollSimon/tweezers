from pathlib import Path


def getSubdirs(path):
    """
    Get all subdirectories

    Args:
        path (:class:`pathlib.Path`): path to get subdirectories from

    Returns:
        :class:`list`
    """

    return [x for x in Path(path).iterdir() if x.is_dir()]
