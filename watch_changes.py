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

from watchdog.observers.fsevents import FSEventsObserver as Observer
from watchdog.events import FileSystemEventHandler

BASEDIR = os.path.abspath(os.path.dirname(__file__))
print >> sys.stdout, "Watching changes to the base directory {}".format(BASEDIR)

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

def getext(filename):
    '''
    Get the file extension.
    '''

    return os.path.splitext(filename)[-1].lower()

class ChangeHandler(FileSystemEventHandler):
    '''
    React to changes in Python and Rest files by
    running unit tests (Python) or building docs (.rst)
    '''
    def on_any_event(self, event):
        '''
        If any file or folder is changed
        '''
        if event.is_directory:
            return
        if getext(event.src_path) == '.py':
            run_behave()
        elif getext(event.src_path) == '.rst':
            build_docs()
        

def main():
    '''
    Called when run as main.
    Look for changes to code and doc files.
    '''

    while 1:
    
        event_handler = ChangeHandler()
        observer = Observer()
        observer.schedule(event_handler, BASEDIR, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

if __name__ == '__main__':
    main()