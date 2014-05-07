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
import platform

if platform.system() is 'Darwin':
    from watchdog.observers.fsevents import FSEventsObserver as Observer
else:
    from watchdog.observers import Observer

from watchdog.events import FileSystemEventHandler

BASEDIR = os.path.abspath(os.path.dirname(__file__))
print("Watching changes to the base directory {}".format(BASEDIR), file=sys.stdout)


def get_now():
    """
    Get the current date and time as a string
    """
    return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")


def build_docs():
    """
    Run the Sphinx build (`make html`) to make sure we have the
    latest version of the docs
    
    Use `call` here so that we don't detect file changes while this
    is running...
    """
    print("Building docs at {0:s}".format(get_now()), file=sys.stderr)
    os.chdir(os.path.join(BASEDIR, "docs"))
    print("Current directory: {}".format(os.getcwd()), file=sys.stderr)
    subprocess.call(r'make html')


def run_unittests():
    """
    Run unit tests with unittest.
    """
    print("Running unit tests at {0:s}".format(get_now()), file=sys.stderr)
    os.chdir(BASEDIR)
    subprocess.call(r'python -m unittest discover -b')


def run_behave():
    """
    Run BDD tests with behave.
    """
    print(u"Running behave at {0:s}".format(get_now()), file=sys.stderr)
    os.chdir(BASEDIR)
    subprocess.call(r'behave')


def get_extension(filename):
    """
    Get the file extension.
    """
    return os.path.splitext(filename)[-1].lower()


class ChangeHandler(FileSystemEventHandler):
    """
    React to changes in Python and Rest files by
    running unit tests (Python) or building docs (.rst)
    """
    def on_any_event(self, event):
        """
        If any file or folder is changed
        """
        if event.is_directory:
            return
        if get_extension(event.src_path) == '.py':
            run_behave()
        elif get_extension(event.src_path) == '.rst':
            build_docs()
        

def main():
    """
    Called when run as main.
    Look for changes to code and doc files.
    """

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
