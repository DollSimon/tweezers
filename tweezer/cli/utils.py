import os
import re

from collections import defaultdict
from itertools import izip

from clint.textui import colored, puts, indent 
from pprint import pprint

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


def pprint_settings(settings, part='all'):
    """
    Pretty terminal printing of tweezer settings stored in json files
    
    :param settings: (dict) with tweezer settings, basically informative key-value pairs
    """
    try:
        if not 'all' in part:
            sections = [k for k in settings.keys() if part in k]
            if sections:
                puts('These are the settings of type {}:\n'.format(colored.blue(part)))
            else:
                puts('No section with this type found in the settings')
                puts('Available sections are: \n')
                for key in settings:
                    print(key)
        else:
            sections = settings.keys()
            puts('These are the {} the settings.\n'.format(colored.blue('all')))

        for section in sections:
            with indent(2):
                puts('Settings of section: {}\n'.format(colored.yellow(section)))

            items = [i for i in settings[section].keys() if 'units' not in i]

            for pos, key in enumerate(items):
                try:
                    this_unit = settings[section]['units'][key]
                    unit = this_unit if this_unit is not None else ''
                    with indent(2):
                        if pos % 2 == 0:
                            puts('{} : {} {}'.format(key, settings[section][key], unit))
                        else:
                            puts('{} : {} {}'.format(colored.white(key), colored.white(settings[section][key]), colored.white(unit)))

                except:
                    with indent(2):
                        if pos % 2 == 0:
                            puts('{} : {}'.format(key, settings[section][key]))
                        else:
                            puts('{} : {}'.format(colored.white(key), colored.white(settings[section][key])))

            puts('\n')
    except:
        pprint(settings, indent=2)




