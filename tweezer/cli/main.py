#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Tweezer Data Analysis on Steroids

Usage: 
  tweezer watch [-t | -m] [<DIR>...] [-l]
  tweezer (analyse | analyze) [-t | -m] <FILE>...
  tweezer convert FILE <LANGUAGE>
  tweezer overview [-t | -m] <DIR>...
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
                puts('tweezer (analyse | analyze) [-t | -m] <FILE>...')
                puts('tweezer convert FILE <LANGUAGE>')
                puts('tweezer overview [-t | -m] <DIR>...')
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
        list_tweezer_files(DIR)
        print('The sun is rising!')
        print('The sun sets!')

