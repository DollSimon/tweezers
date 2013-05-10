#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Monitors our code & docs for changes

To get coverage:

    python -m coverage run -m unittest discover
    python -m coverage report -m
        Or: `python -m coverage html`

"""

import os
import sys
import subprocess
import datetime
import time
import re

from watchdog.observers.fsevents import FSEventsObserver as Observer
from watchdog.events import FileSystemEventHandler

from tweezer.core.parsers import classify

BASEDIR = os.path.abspath(os.path.dirname(__file__))
print >> sys.stdout, "Watching changes to the base directory {}".format(BASEDIR)

TWEEBOT_DATA_PATTERN = re.compile(r"(\d)+.(datalog)(.\d+)+.(datalog)(.txt)", re.IGNORECASE)
TWEEBOT_STATS_PATTERN = re.compile(r"(\d)+.(tweebotstats)(.txt)", re.IGNORECASE)
TWEEBOT_LOGS_PATTERN = re.compile(r"(\d)+.(tweebotlog)(.\d+)+(.txt)", re.IGNORECASE)

def find_files(files, regex_pattern, verbose=False):
    """
    Finds all files in a list that matches a certain pattern.

    Parameters:
    -----------
        files           : list of files
        regex_pattern   : regular expression pattern
        verbose         : whether or not to print extra information

    Returns:
    --------
        files_found     : list of files that matches the pattern

    """
    files_found = []
    
    for iFile in files:
        match = re.findall(regex_pattern, iFile)
        if match:
            files_found.append(iFile)
            if verbose:
                print("Found file: {}".format(iFile))

        else:
            if verbose:
                print("Pattern not found!")
        
    return files_found

def get_now():
    '''
    Get the current date and time as a string
    '''
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def build_docs():
    '''
    Run the Sphinx build (`make html`) to make sure we have the
    latest version of the docs
    
    Use `call` here so that we don't detect file changes while this
    is running...
    '''

    print >> sys.stderr, "Building docs at %s" % get_now()
    os.chdir(os.path.join(BASEDIR, "docs"))
    print >> sys.stderr, "Current directory: {}".format(os.getcwd())
    subprocess.call(r'make html')

def run_unittests():
    '''
    Run unit tests with unittest.
    '''
    print >> sys.stderr, "Running unit tests at %s" % get_now()
    os.chdir(BASEDIR)
    subprocess.call(r'python -m unittest discover -b')

def run_behave():
    '''
    Run BDD tests with behave.
    '''
    print >> sys.stderr, "Running behave at %s" % get_now()
    os.chdir(BASEDIR)
    subprocess.call(r'behave')

def get_type(file_name):
    """
    Get the file type and other attributes
    """
    file_type = classify(file_name)
    return os.path.splitext(file_name)[-1].lower()


class ChangeHandler(FileSystemEventHandler):
    '''
    React to changes in Python and Rest files by
    running unit tests (Python) or building docs (.rst)
    '''
    def on_any_event(self, event):
        '''
        If any file or folder is changed
        '''
        print(event.event_type)
        if event.is_directory:
            print("Something connected to directories")
            return
        if get_type(event.src_path) == '.py':
            run_behave()
        elif get_type(event.src_path) == '.rst':
            build_docs()
        elif get_type(event.src_path) == '.txt':
            print("Hurray")
        elif get_type(event.src_path) == '.groovy':
            print("A new groovy file")
            print(event.src_path)
        

def run_watcher(directory):
    '''
    Called when run as main.
    Look for changes to code and doc files.
    '''

    while 1:
    
        event_handler = ChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, directory, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == '__main__':
    sys.exit(run_watcher(BASEDIR))
