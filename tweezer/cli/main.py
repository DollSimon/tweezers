#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Tweezer Data Analysis on Steroids

Usage: 
  tweezer watch [-t | -m] [<DIR>...] [-l]
  tweezer (analyse | analyze) [-t | -m] [<FILE>...]
  tweezer convert [<FILE>...] <LANGUAGE>
  tweezer overview [-t | -m] ([<DIR>...] | -f [<FILE>...])
  tweezer list [<DIR>...]
  tweezer (-h | --help)
  tweezer (-v | --version)

Commands:
  watch         Monitor directory for changes
  analyse       Perform specified data analysis
  analyze       Perform specified data analysis
  convert       Convert data to be able to work in specified language
  overview      Produce "Overview.pdf" for data files in directory
  list          List all files and file types in a directory recursively

Arguments:
  FILE          Input file
  PATH          Out directory
  DIR           Input directory
  LANGUAGE      Preferred language or data container 

Options:
  -h --help     Show this screen
  -v --version  Show version number
  -t --tweebot  Tweebot tweezer mode
  -m --manual   Manual tweezer mode
  -l --logging  Write log file
  -f --file     Switch to file mode when input can be file or dir

"""
import os
import sys

from docopt import docopt
from clint import args 
from clint.textui import colored, puts, indent 
from termcolor import cprint

from tweezer import __version__
try:
    from tweezer.core.polymer import ExtensibleWormLikeChain as WLC 
    from tweezer.core.watcher import run_watcher
    from tweezer.cli.utils import list_tweezer_files
    from tweezer.core.overview import full_tweebot_overview, tweebot_overview
except ImportError:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('Please check installation instructions @ {}'.format(colored.yellow('http://bitbucket.org/majahn/tweezer')))
    exit()


VERSION = ".".join(str(x) for x in __version__)


def start():

    args = docopt(__doc__, version=VERSION, help=False)

    puts('\n{}'.format(colored.red('Development: Show arguments')))
    print(args)
    puts('')

    # Getting help
    if args['--help']:
        puts('{0} : {1}'.format(
            colored.blue('tweezer'),
            'A data analysis tool for single-molecule experiments'))
        puts('')
        puts('{0}: http://bitbucket.org/majahn/tweezer @ version {1}'.format(
            colored.yellow('Source'),
            VERSION))
        puts('')

        puts(colored.white('Tweezer Data Analysis Command Line Interface'))

        with indent(2):
            puts('\n{}:'.format(colored.green('Usage')))
            with indent(2):
                puts('tweezer watch [-t | -m] [<DIR>...] [-l]')
                puts('tweezer (analyse | analyze) [-t | -m] [<FILE>...]')
                puts('tweezer convert [<FILE>...] <LANGUAGE>')
                puts('tweezer overview [-t | -m] ([<DIR>...] | -f [<FILE>...])')
                puts('tweezer list [<DIR>...]')
                puts('tweezer (-h | --help)')
                puts('tweezer (-v | --version)')
              
            puts('\n{}:'.format(colored.green('Commands')))
            with indent(2):
                puts('watch         Monitor directory for changes')
                puts('analyse       perform specified data analysis')
                puts('analyze       Perform specified data analysis')
                puts('convert       Convert data to be able to work in specified language')
                puts('overview      Produce "Overview.pdf" for data files in directory')
                puts('list          List all files and file types in a directory recursively')

            puts('\n{}:'.format(colored.green('Arguments')))
            with indent(2):
                puts('FILE          Input file')
                puts('PATH          Out directory')
                puts('DIR           Input directory')
                puts('LANGUAGE      Preferred language or data container')

            puts('\n{}:'.format(colored.green('Options')))
            with indent(2):
                puts('-h --help     Show this screen')
                puts('-v --version  Show version number')
                puts('-t --tweebot  Tweebot tweezer mode')
                puts('-m --manual   Manual tweezer mode')
                puts('-l --logging  Write log file')
                puts('-l --logging  Write log file')
                puts('-f --file     Switch to file mode when input can be file or dir')
          
    # Checking and setting default values
    if not args['--tweebot'] and not args['--manual']:
        args['--tweebot'] = True

    # tweezer analyse | analyze
    if args['analyse'] or args['analyze']: 
        puts('{}'.format(args['<FILE>']))
        puts('i{}V'.format(colored.red('Rackooon')))
        puts('This is {}'.format(os.path.dirname(os.path.abspath(__file__))))
        puts(''.format(colored.green('Rackooon')))
        puts('Test')
        puts('First argument is {}'.format(sys.argv[0]))
        puts('Second argument is {}'.format(sys.argv[1]))
        puts('Third argument is {}'.format(sys.argv[2]))

    # tweezer watch
    if args['watch']:

        # check directory
        if not args['<DIR>']:
            args['<DIR>']= os.getcwd()

        DIR = args['<DIR>']

        with indent(2):
            puts('Calling tweezer watch from {}\n'.format(colored.green(DIR)))
            puts('To stop this script hit {}.'.format(colored.red("CTRL + C")))
            
        run_watcher(DIR)

    # tweezer list
    if args['list']:

        # check directory
        if not args['<DIR>']:
            args['<DIR>']= os.getcwd()

        DIR = args['<DIR>']

        puts('Calling tweezer list from {}'.format(colored.green(DIR)))
        files = list_tweezer_files(DIR)
        print('The sun is rising!')
        print('There are {} file types'.format(len(files)))
        print('There are the following types: {} '.format(len(files)))
        puts('Here is the result: {}'.format(colored.blue(files)))
        print('The sun sets!')

    # tweezer overview
    if args['overview']:

        # check directory
        if not args['<DIR>']:
            args['<DIR>']= os.getcwd()

        DIR = args['<DIR>']

        # check file input
        if args['--file']:
            FILES = args['<FILE>']
        else:
            FILES = None

        if FILES:
            for f in FILES:
                path = os.path.join(DIR, f)
                tweebot_overview(path)

        puts('Calling tweezer overview from {}'.format(colored.green(DIR)))
        full_tweebot_overview(DIR)
