from pathlib import Path
import re
from collections import OrderedDict


def getFiles(path, suffix=None, prefix=None, parent=None, recursive=False, hiddenFiles=False):
    """
    Recursively get all files in the given path. If suffix, prefix or parent are set, only files
    meeting these conditions are returned. Hidden files can be excluded and the search can be performed recursively.

    Args:
        path (:class:`pathlib.Path` or :class:`str`): path to the directory to check recursively
        suffix (str): filter by file suffix (default: None)
        prefix (str): filter by file prefix (default: None)
        parent (str): filter by parent directory name (default: None)
        recursive (bool): descent into child directories?
        hiddenFiles (bool): include hidden files?

    Returns:
        :class:`list` of :class:`pathlib.Path`
    """

    # check if the input is a Path object (or inherited from it, i.e. is an instance of it)
    if not isinstance(path, Path):
        # try to convert it
        path = Path(path)

    # store result
    res = []

    # check each element in the current directory
    for element in path.iterdir():
        if element.is_dir() and recursive:
            # recursively call the function on subdirectories
            res += getFiles(element, suffix=suffix, prefix=prefix, parent=parent, recursive=recursive,
                             hiddenFiles=hiddenFiles)
        else:
            # store the element
            candidate = element
            # check all conditions and reset candidate if one of them fails
            if suffix is not None and not element.name.endswith(suffix):
                candidate = None
            elif parent is not None and element.parts[-2] != parent:
                candidate = None
            elif prefix is not None and not element.parts[-1].startswith(prefix):
                # special case for hidden files: the prefix starts after the '.'
                if hiddenFiles and element.parts[-1].startswith('.' + prefix):
                    pass
                else:
                    candidate = None
            elif not hiddenFiles and element.parts[-1].startswith('.'):
                candidate = None

            if candidate:
                res.append(candidate)

    return res


def getSimilarFiles(path, foldersApart=0, categories=[], discardIncomplete=True):
    """
    Recursively find similar files in the given path. Files are found using :func:`ixo.file.getFiles` based on the
    prefix and suffix pairs given in ``categories``. Two files are similar if they share the same `name core`,
    i.e. their name is the same after prefix and suffix were stripped. Also, they must share the same folder
    structure minus the number of parent folders set by ``foldersApart``.

    Example:
        If ``foldersApart`` is 0, then only files. If it is 1, they must share the same parent folder and so on.
        In fact, the :attr:`pathlib.PurePath.parents` attribute is compared with parameter ``foldersApart``.

    Args:
        path (:class:`pathlib.Path` or :class:`str`): path to search for files
        foldersApart (int): number of parent folders that are allowed to differ
        categories (:class:`list`): list of prefix and suffix pairs that are passed to :func:`ixo.file.getFiles`
        discardIncomplete (bool): remove found files from the results list if they do not contain a file from each of
                                  the given categories

    Returns:
        :class:`list` of :class:`list` of :class:`pathlib.Path`
    """

    files = OrderedDict()
    for category in categories:
        foundFiles = getFiles(path, prefix=category[0], suffix=category[1], recursive=True, hiddenFiles=False)
        # create regex string for core name extraction
        reStr = '^'
        if category[0]:
            reStr += re.escape(category[0])
        reStr += '(.*)'
        # deprecated: kept here in case some code relies on it and it needs reactivation, delete after Jan 2016
        # add optional stuff to be cut from the end
        # reStr += '(' + cutFromEnd + ')?'
        if category[1]:
            reStr += re.escape(category[1])
        reStr += '$'
        # add to dictionary: key is the Path object of the file and value its core name (name without prefix and suffix)
        for file in foundFiles:
            files[file] = re.sub(reStr, '\g<1>', file.name)

    matchedFiles = []
    try:
        file, coreName = files.popitem()
    except KeyError:
        return matchedFiles
    # for each file...
    while file:
        match = [file]
        # check if there are similar files
        for cFile, cCoreName in files.items():
            if coreName != cCoreName:
                continue
            elif file.parents[foldersApart] != cFile.parents[foldersApart]:
                continue
            # append matched file to list
            match.append(cFile)
        # remove matched files from 'files' dict => each file can only be matched once
        for key in match[1:]:
            files.pop(key)
        matchedFiles.append(match)

        # get next item
        try:
            file, coreName = files.popitem()
        except KeyError:
            file = False

    # sort resulting list
    for res in matchedFiles:
        res.sort()

    # discard all sublists that do not have the proper number of files
    if discardIncomplete:
        for key in matchedFiles:
            if len(matchedFiles[key]) is not len(categories):
                matchedFiles.pop(key)

    return matchedFiles
