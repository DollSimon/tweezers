"""
General utility functions used for tweezer package.

"""
import os
import cProfile


def profile_this(fn):
    """
    Decorator to profile the execution time of a function
    
    :param fn: function to be profiled
    """
    def profiled_fn(*args, **kwargs):
        # name of profile dump
        fpath = fn.__name__ + ".profile"
        prof = cProfile.Profile()
        ret = prof.runcall(fn, *args, **kwargs)
        prof.dump_stats(fpath)
        return ret
    return profiled_fn
    

def get_subdirs(path, is_file=True):
    """
    Splits a path into its subdirectories and returns a list of those 

    :param path: file path
    :param is_file: (Boolean) defaults to True for a complete file_name 

    :return subdirs: List of subdirectories that make up a path
    """
    if is_file:
        _path = os.path.dirname(path)
    else:
        _path = path

    subdirs = []
    while True:
        _path, folder = os.path.split(_path)

        if folder!="":
            subdirs.append(folder)
        else:
            if _path!="":
                subdirs.append(_path)
            break

    subdirs.reverse()

    return subdirs


def get_parent_directory(file_name):
    """
    Extracts the parent directory of a file from an absolute path 

    :param file_name: (Path)

    :return parent_dir: (String) name of parent directory
    """
    return get_subdirs(file_name)[-1]


class VersionChecker(object):

    """
    Keeps track of the code history that is used to analyse the data.

    """

    def __init__(self, python_function):
        self.python_function = python_function

