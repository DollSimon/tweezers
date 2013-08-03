import os, sys
import re

import hashlib

import envoy

from collections import defaultdict, namedtuple
from itertools import izip
from copy import deepcopy

from clint.textui import colored, puts, indent 
from pprint import pprint

try:
    import simplejson as json
except ImportError:
    import json

try:
    from tweezer.ixo.os_ import generate_file_tree_of
    from tweezer.core.parsers import classify_all, parse_tweezer_file_name
    from tweezer.cli import InterpretUserInput
    from tweezer import read
except ImportError, err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')

CACHING_FILE = 'cached_file_listing.json'

def list_tweezer_files(directory, cache_results=True):
    """ 
    Walks a directory structure top-down, registering known tweezer file types along the way. 

    :param directory: (Path) starting directory

    :return files: (defaultdict) where keys are file types and values are corresponding files specified by their full path

    """
    cached_results_file = os.path.join(directory, CACHING_FILE)  

    files = defaultdict(list)

    if os.path.exists(cached_results_file):

        # check if length of files in cache equals length os files found. 
        current_directory_state = get_directory_state(directory)

        with open(cached_results_file, 'r') as f:
            cached_data = json.load(f)

        if current_directory_state == cached_data['directory_state']:
            for k, v in cached_data.iteritems():
                files[k] = v   
        else:
            current_directory_state = get_directory_state(directory)

            file_names = list(generate_file_tree_of(directory))

            types = classify_all(file_names)
            for t, f in izip(types, file_names):
                files[t.lower()].append(f)

            files['directory_state'] = current_directory_state

            with open(cached_results_file, 'w') as f:
                json.dump(files, f, indent=2)

    else:
        directory_state = get_directory_state(directory)

        file_names = list(generate_file_tree_of(directory))

        types = classify_all(file_names)
        for t, f in izip(types, file_names):
            files[t.lower()].append(f)

        files['directory_state'] = directory_state

        if cache_results:
            with open(cached_results_file, 'w') as f:
                json.dump(files, f, indent=2)

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
        trial_name = "_".join([str(trial), str(subtrial)])
    else:
        trial_name = str(trial)

    for t, f in files.iteritems():
        for x in f:
            if re.search('^\s*[a-zA-Z_]*{}\W'.format(trial_name), os.path.basename(x)):
                trial_files[t].append(x)
        else:
            if not trial_files.has_key(t):
                trial_files[t].append(None)

    return trial_files


def sort_files_by_trial(files=defaultdict(list), sort_by=None, clean=True):
    """
    Sorts a dictionary of all tweezer files into a dictionary that splits 
    according to all files found for specified key
    
    :param files: (defaultdict) of all files found in the current directory tree
    :param sort_by: (str) specifying the file type to use for the sorting 

    :return trial_files: (dict) of 
    
    .. note::

        The reason for this is that there are many more log files written than 
        data files. Like this you can either look at the successful trials or 
        all trials, depending on your needs
    """
    # try to infer the sorting key
    if not sort_by:
        if len(files.get('man_data', [])) >= len(files.get('bot_data', [])):
            sort_by = 'man_data'
        else:
            sort_by = 'bot_data'
         
    FileInfos = [parse_tweezer_file_name(f, parser=sort_by) for f in files[sort_by]]
    trials = [(f.trial, f.subtrial) for f in FileInfos]

    trial_files = {}
    for t in trials:
        if t[1] is None:
            trial_files[t[0]] = collect_files_per_trial(files=files, trial=int(t[0]))
        else:
            trial_files["_".join([t[0], t[1]])] = collect_files_per_trial(files=files, trial=int(t[0]), subtrial=t[1])

    if clean:
        cleaned_trials = {}

        for trial, files in trial_files.iteritems():

            cleaned_files = {}

            for ftype, fpaths in dict(files).iteritems():
                if fpaths:
                    if fpaths[0] is not None:
                        if len(fpaths) == 1:
                            cleaned_files[ftype] = fpaths[0]
                        else:
                            cleaned_files[ftype] = fpaths

            cleaned_trials[trial] = cleaned_files 

        trial_files = cleaned_trials

    return trial_files


def collect_data_per_trial(trial_files):
    """
    Collects most important data for one trial

    :param trial_files: (defaultdict) that holds the files collected per trial

    :return TrialData: (namedtuple) that holds relevant data
    """
    def namedtuple_factory(files, data):
        fields = [k for k in files]
        TrialData = namedtuple('TrialData', fields) 
        return TrialData(*data)

    try:
        files = []
        data = []
        for ftype, fpath in trial_files.iteritems():
            files.append(ftype)
            data.append(read(fpath))

        TrialData = namedtuple_factory(files, data)
    except:
        raise

    return TrialData


def pprint_settings(settings, part='all', status='current', other_settings={}, other_status='default'):
    """
    Pretty terminal printing of tweezer settings stored in json files
    
    :param settings: (dict) with tweezer settings, basically informative key-value pairs

    :param part: (str) which signifies sections of overall settings

    :param status: (str) to be used in display information

    :param other_settings: (dict) of different tweezer settings to be compared with the values in settings
    """
    try:
        if not 'all' in part:
            sections = [k for k in settings.keys() if part in k]
            if sections:
                with indent(2):
                    puts('These are the {s} settings of type {p}:\n'.format(p=colored.blue(part), s=status))
            else:
                with indent(2):
                    puts('No section with this type found in the {} settings'.format(status))
                    puts('Available sections are: \n')
                    for key in settings:
                        print(key)
        else:
            sections = settings.keys()
            with indent(2):
                puts('These are {p} the {s} settings.\n'.format(p=colored.blue('all'), s=status))

        # printing
        for section in sections:
            with indent(2):
                puts('Settings of section: {}\n'.format(colored.yellow(section)))

            items = [i for i in settings[section].keys() if 'units' not in i]

            for pos, key in enumerate(items):
                try:
                    this_unit = settings[section]['units'][key]
                    unit = this_unit if this_unit is not None else ''

                    if not other_settings:
                        with indent(2):
                            if pos % 2 == 0:
                                puts('{} : {} {}'.format(key, settings[section][key], unit))
                            else:
                                puts('{} : {} {}'.format(colored.white(key), colored.white(settings[section][key]), colored.white(unit)))
                    else:
                        with indent(2):
                            if pos % 2 == 0:
                                try:
                                    value = settings[section][key]
                                    puts('{key} : {value} {unit} {spacing}({other_setting}: {other_value})'.format(
                                        key = key, 
                                        value = settings[section][key], 
                                        unit = unit, 
                                        spacing = flexible_tab(' '.join([' : '.join([key, str(value)]), unit])), 
                                        other_setting = colored.yellow(other_status), 
                                        other_value = colored.yellow(other_settings[section][key])))
                                except:
                                    puts('{} : {} {}'.format(key, settings[section][key], unit))
                            else:
                                try:
                                    value = settings[section][key]
                                    puts('{key} : {value} {unit} {spacing}({other_setting}: {other_value})'.format(
                                        key = colored.white(key), 
                                        value = colored.white(settings[section][key]), 
                                        unit = colored.white(unit), 
                                        spacing = flexible_tab(' '.join([' : '.join([key, str(value)]), unit])), 
                                        other_setting = colored.yellow(other_status), 
                                        other_value = colored.yellow(other_settings[section][key])))
                                except:
                                    puts('{} : {} {}'.format(colored.white(key), colored.white(settings[section][key]), colored.white(unit)))
                except:
                    if not other_settings:
                        with indent(2):
                            if pos % 2 == 0:
                                puts('{} : {}'.format(key, settings[section][key]))
                            else:
                                puts('{} : {}'.format(colored.white(key), colored.white(settings[section][key])))
                    else:
                        with indent(2):
                            if pos % 2 == 0:
                                try:
                                    value = settings[section][key]
                                    puts('{key} : {value} {spacing}({other_setting}: {other_value})'.format(
                                        key = key, 
                                        value = settings[section][key], 
                                        spacing = flexible_tab(' : '.join([key, str(value)])), 
                                        other_setting = colored.yellow(other_status), 
                                        other_value = colored.yellow(other_settings[section][key])))
                                except:
                                    puts('{} : {}'.format(key, settings[section][key]))
                            else:
                                try:
                                    value = settings[section][key]
                                    puts('{key} : {value} {spacing}({other_setting}: {other_value})'.format(
                                        key = colored.white(key), 
                                        value = colored.white(settings[section][key]), 
                                        spacing = flexible_tab(' : '.join([key, str(value)])), 
                                        other_setting = colored.yellow(other_status), 
                                        other_value = colored.yellow(other_settings[section][key])))
                                except:
                                    puts('{} : {}'.format(colored.white(key), colored.white(settings[section][key])))

            puts('\n')
    except:
        pprint(settings, indent=2)


def update_settings(file_name='settings.json', old_settings={}, part='all', **kwargs):
    """
    Command line interface to update a standard tweezer .json settings or configuration file. 
    
    :param file_name: (path) .json file to update [default = 'settings.json']

    :param old_settings: (dict) standard tweezer settings dictionary with sections and units

    :param part: (str) part or section of the settings file to be exposed to the update routine [default = 'all']
    """
    if not 'all' in part:
        sections = [k for k in old_settings.keys() if part in k]
        if sections:
            pprint_settings(old_settings, part=part, status='current')
        else:
            puts('No section with this type found in the current settings')
            puts('Available sections are: \n')
            for key in old_settings:
                print(key)

            want_new_section = raw_input('Do you want to add a new section to {}?'.format(os.path.basename(file_name)))

            if InterpretUserInput[want_new_section]:
                pass

    else:
        sections = old_settings.keys()
        pprint_settings(old_settings, part=part, status='current')

    # updating
    try:
        new_settings = deepcopy(old_settings)
        for section in sections:
            with indent(2):
                puts('Updating settings of section: {}\n'.format(colored.yellow(section)))

            items = [i for i in new_settings[section].keys() if 'units' not in i]

            for pos, key in enumerate(items):
                try:
                    this_unit = new_settings[section]['units'][key]
                    unit = this_unit if this_unit is not None else ''
                    with indent(2):
                        puts('Update {} : {} {}'.format(key, new_settings[section][key], unit))
                        while True:
                            new_value = raw_input('> {} = '.format(colored.yellow(key)))
                            puts('')

                            if not new_value:
                                break

                            # parse string value
                            if re.search('^\d+$', new_value.strip()):
                                new_value = int(new_value)
                            elif re.search('^\d+\.\d+$', new_value.strip()) or re.search('^\d+e[-0-9]\d*$', new_value.strip()):
                                new_value = float(new_value)
                            else:
                                new_value = new_value.strip()

                            # assign value
                            if new_value:
                                if type(new_value) is type(new_settings[section][key]):
                                    new_settings[section][key] = new_value
                                    break
                                else:
                                    puts('Sorry, wrong type. {} is of type {}'.format(key, type(new_settings[section][key])))
                                    try_again = raw_input('> Try again? (y | n): ')
                                    if InterpretUserInput[try_again]:
                                        continue
                                    else:
                                        break
                except:
                    with indent(2):
                        puts('Update {} : {}'.format(key, new_settings[section][key]))
                        while True:
                            new_value = raw_input('> {} = '.format(colored.yellow(key)))
                            puts('')

                            if not new_value:
                                break

                            # parse string value
                            if re.search('^\d+$', new_value.strip()):
                                new_value = int(new_value)
                            elif re.search('^\d+\.\d+$', new_value.strip()) or re.search('^\d+e[-0-9]\d*$', new_value.strip()):
                                new_value = float(new_value)
                            else:
                                new_value = new_value.strip()

                            # assign value
                            if new_value:
                                if type(new_value) is type(new_settings[section][key]):
                                    new_settings[section][key] = new_value
                                    break
                                else:
                                    puts('Sorry, wrong type. {} is of type {}'.format(key, type(new_settings[section][key])))
                                    try_again = raw_input('> Try again? (y | n): ')
                                    if InterpretUserInput[try_again]:
                                        continue
                                    else:
                                        break
            puts('')

    except (KeyboardInterrupt, SystemExit), e:
        new_settings = deepcopy(old_settings)
        raise e

    # persistence
    pprint_settings(new_settings, part=part, status='new', other_settings=old_settings, other_status='old')

    with open(file_name, 'w') as f:
        f.write(json.dumps(new_settings, indent=2, separators=(',', ': ')))


def flexible_tab(key):
    if len(key) in range(63, 300):
        spacing = ''
    if len(key) in range(56, 63):
        spacing = '\t'
    elif len(key) in range(49, 56):
        spacing = '\t\t'
    elif len(key) in range(42, 49):
        spacing = '\t\t\t'
    elif len(key) in range(35, 42):
        spacing = '\t\t\t\t'
    elif len(key) in range(28, 35):
        spacing = '\t\t\t\t\t'
    elif len(key) in range(21, 28):
        spacing = '\t\t\t\t\t\t'
    elif len(key) in range(14, 21):
        spacing = '\t\t\t\t\t\t\t'
    elif len(key) in range(2, 14):
        spacing = '\t\t\t\t\t\t\t\t'
    else:
        spacing = ''

    return spacing


def get_directory_state(directory=None):
    """
    Calls the underlying os to get a unique number for the content of the directory.

    :param (directory): (path) of the directory to be studied recursively

    :return md5: (md5) unique sha number that encrypts the directory state
    """
    if not directory:
        directory = os.getcwd()

    names_call = envoy.run('find {dir} -type f -exec stat -f "%N" {placeholder} \\;'.format(
        dir = directory, 
        placeholder ='{}'))

    sizes_call = envoy.run('find {dir} -type f -exec stat -f "%z" {placeholder} \\;'.format(
        dir = directory, 
        placeholder ='{}'))

    names = names_call.std_out
    sizes = sizes_call.std_out

    try:
        return hashlib.sha256(names + sizes).hexdigest()
    except:
        raise


def main():
    os.chdir('/Users/jahnel/code/example_data/manual/')
    directory = os.getcwd()
    files = list_tweezer_files(directory)
    print(len(files))


if __name__ == '__main__':
    sys.exit(main())
