#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Monitors a tweezer directory for file changing events

"""

import os
import sys
import subprocess
import datetime
import time
import re

import macropy.core.macros

from collections import deque
from Queue import Queue

from watchdog.observers.fsevents import FSEventsObserver as Observer
from watchdog.events import FileSystemEventHandler

from clint.textui import colored, puts, indent 
from termcolor import cprint

from tweezer.core.parsers import classify

BASEDIR = os.path.abspath(os.path.dirname(__file__))

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
    """
    Reacts to changes on the file system and dispatches the appropriate methods for the registered file system event.
    """
    def __init__(self):
        super(ChangeHandler, self).__init__()
        self.dataq = deque()
        self.logq = deque()

    def on_created(self, event):
        """
        If any file or directory is on_created
        """
        if event.is_directory:
            print("The directory {} has been {}".format(colored.red(event.src_path), colored.blue(event.event_type)))
            return
            
        file_type = classify(event.src_path)
        event_type = event.event_type

        print("A {} file has been {}".format(colored.red(file_type), colored.blue(event_type)))

        if file_type == 'BOT_DATA':
            print('Data file event')
            self.dataq.append(event.src_path)
            if len(self.dataq) > 1:
                # print(list(self.dataq))
                print("More than one data file registered.")

        if file_type == 'BOT_LOG':
            print('Log file event')
            self.logq.append(event.src_path)
            if len(self.logq) > 1:
                print("More than one log file registered.")
                # print(list(self.logq))


def run_watcher(directory):
    '''
    Called when run as main() from the command line.
    Looks for changes to the file system.
    Can be stopped with CTRL+C.
    '''

    data_files = Queue()

    while True:
    
        event_handler = ChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, directory, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(10)
                print(event_handler.dataq)
                print("I'm accessing the queue from outside")
                print(event_handler.dataq)
        except (KeyboardInterrupt, SystemExit) as close:
            q = observer.event_queue
            observer.stop()
            with indent(2):
                puts("\n{}\n".format(colored.white('Thanks for watching...')))
                puts("{}\n".format(colored.white('Finishing up...')))
                puts("Files left in the data queue: {}".format(colored.magenta(len(event_handler.dataq))))
            print("The stored values are {}".format(event_handler.dataq))
            return
        observer.join()

if __name__ == '__main__':
    sys.exit(run_watcher(BASEDIR))
