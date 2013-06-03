import os
import re

from collections import defaultdict
from itertools import izip

from tweezer.core.parsers import classify_all


def list_tweezer_files(directory):
    """ 
    Walks a directory structure top-down, registering known tweezer file types along the way. 

    :param directory: (Path) starting directory

    :return files: (defaultdict) where keys are file types and values are corresponding files

    """
    files = defaultdict(list)

    for (path, dirs, file_names) in os.walk(directory):
        types = classify_all(file_names)
        for t, f in izip(types, file_names):
            files[t.lower()].append(f)

    return files


def file_cache(parameter):
    """
    Short description 

    :param parameter: Description

    :return name: Description
    """
    pass


def collect_files_per_trial(trial=1, subtrial=None, files=defaultdict(list)):
    """
    Collects all files corresponding to one experiment based on trial and subtrial number.
    
    :param trial: (int) specifies the trial number

    :param subtrial: (str) specifies the subtrial in a file name pattern such as '1_a...'

    :param files: (defaultdict) of all files found in the current directory tree
    
    :return trial_files: (defaultdict) that stores all files connected to one experiment
    
    """
    trial_files = defaultdict(list)

    if subtrial:
        trial_name = "_".join(str(trial), str(subtrial))
    else:
        trial_name = str(trial)

    for t, f in files.iteritems():
        for x in f:
            if re.search('^\s*{}\W'.format(trial_name), x):
                trial_files[t].append(x)
        else:
            if not trial_files.has_key(t):
                trial_files[t].append(None)

    return trial_files
