#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Tweezer Data Analysis on Steroids

Usage: 
  tweezer watch [-t | -m] [<DIR>...] [-l]
  tweezer (analyse | analyze) [-t | -m] <FILE>...
  tweezer convert FILE <LANGUAGE>
  tweezer overview [-t | -m] <DIR>...
  tweezer (-h | --help)
  tweezer (-v | --version)

Commands:
  watch         Monitor directory for changes
  analyse       Perform specified data analysis
  analyze       Perform specified data analysis
  convert       Convert data to be able to work in specified language
  overview      Produce "Overview.pdf" for data files in directory

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

from docopt import docopt
from tweezer import __version__
from clint import args 
from clint.textui import colored, puts, indent 
from termcolor import cprint

# try:
#     from tweezer.core.polymer import ExtensibleWormLikeChain as WLC 
#     from tweezer.core.watcher import run_watcher
# except ImportError:
#     exit('This program requires the installation of the tweezer package.') 


def start():
    cprint("Rackoon new", "red")
    version = ".".join(str(x) for x in __version__)

    puts('{0} @ version {1} by Marcus Jahnel, Grill-Lab {2}'.format(
            colored.blue('tweezer'),
            version,
            colored.green('jahnel@mpi-cbg.de')))
    puts('{0}: http://bitbucket.org/majahn/tweezer'.format(colored.yellow('source')))

    puts('{}'.format(colored.magenta('A tool for data analysis.')))
    puts('{}'.format(colored.green('A tool for data analysis.')))
    puts('{}'.format(colored.cyan('A tool for data analysis.')))
    puts('{}'.format(colored.yellow('A tool for data analysis.')))
    puts('{}'.format(colored.red('A tool for data analysis.')))
    puts('{}'.format(colored.black('A tool for data analysis.')))
    puts('{}'.format(colored.white('A tool for data analysis.')))
    puts('{}'.format(colored.clean('A tool for data analysis.')))
    puts('{}'.format(colored.blue('A tool for data analysis.')))

    puts('\n{0}:'.format(colored.cyan('tentacles')))
    args = docopt(__doc__, version=version)


    puts('{0}. version {1} by Grill-Lab {2}'.format(
            colored.blue('tweezer'),
            version(),
            colored.green('jahnel@mpi-cbg.de')))
    puts('{0}: http://bitbucket.org/majahn/tweezer'.format(colored.yellow('source')))

    puts('\n{0}:'.format(colored.cyan('tentacles')))

    with indent(4):
        puts(colored.green('octogit login'))
        puts(colored.green("octogit create <repo> 'description'"))
        puts(colored.green("octogit create <repo> 'description' <organization>"))
        puts(colored.green('octogit issues [--assigned]'))
        puts(colored.green('octogit issues'))
        puts(colored.green("octogit issues create 'issue title' 'description'"))
        puts(colored.green('octogit issues <number>'))
        puts(colored.green('octogit issues <number> close'))
        puts(colored.green('octogit issues <number> view'))
        puts('\n')

    # print(args)

    # Checking and setting default values
    if not args['--tweebot'] and not args['--manual']:
        args['--tweebot'] = True

    # print(args)

    # tweezer analyse | analyze
    if args['analyse'] or args['analyze']:
        cprint('Rocket', 'green')

    # tweezer watch
    if args['watch']:

        # check directory
        if not args['<DIR>']:
            args['<DIR>']= os.getcwd()

        print('The sun is rising!')
        run_watcher()
        print('The sun sets!')

    print(args)
