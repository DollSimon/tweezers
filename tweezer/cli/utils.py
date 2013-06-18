import os
import re

from collections import defaultdict
from itertools import izip

from tweezer.core.parsers import classify_all, parse_tweezer_file_name


def list_tweezer_files(directory):
    """ 
    Walks a directory structure top-down, registering known tweezer file types along the way. 

    :param directory: (Path) starting directory

    :return files: (defaultdict) where keys are file types and values are corresponding files specified by their full path

    """
    files = defaultdict(list)

    for (path, dirs, file_names) in os.walk(directory):
        types = classify_all(file_names)
        for t, f in izip(types, file_names):
            files[t.lower()].append(os.path.join(directory, path, f))

    return files


def file_cache(parameter):
    """
    Short description 

    :param parameter: Description

    :return name: Description
    """
    pass


def collect_files_per_trial(files=defaultdict(list), trial=1, subtrial=None):
    """
    Collects all files corresponding to one experiment based on trial and subtrial number.
    
    :param files: (defaultdict) of all files found in the current directory tree

    :param trial: (int) specifies the trial number

    :param subtrial: (str) specifies the subtrial in a file name pattern such as '1_a...'
    
    :return trial_files: (defaultdict) that stores all files connected to one experiment
    
    """
    trial_files = defaultdict(list)

    if subtrial:
        trial_name = "_".join(str(trial), str(subtrial))
    else:
        trial_name = str(trial)

    for t, f in files.iteritems():
        for x in f:
            if re.search('^\s*{}\W'.format(trial_name), os.path.basename(x)):
                trial_files[t].append(x)
        else:
            if not trial_files.has_key(t):
                trial_files[t].append(None)

    return trial_files


def sort_tweebot_trials(files=defaultdict(list), sort_by='bot_data'):
    """
    Sorts a dictionary of all tweezer files into a dictionary that splits according to all files found for specified key
    
    :param files: (defaultdict) of all files found in the current directory tree
    :param sort_by: (str) specifying the file type to use for the sorting 

    :return trial_files: (dict) of 
    
    .. note::

        The reason for this is that there are many more log files written than data files. Like this you can either look at the successful trials or all trials, depending on your needs
    """
    trials = [int(parse_tweezer_file_name(f, parser=sort_by).trial) for f in files[sort_by]]

    trial_files = {}
    for t in trials:
        trial_files[t] = collect_files_per_trial(files=files, trial=t)

    return trial_files


def print_default_settings():
    pass 



