#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Tweezer Data Analysis on Steroids

Usage:
  tweezer watch [-t | -m] [<DIR>...] [-l]
  tweezer (analyse | analyze) [-t | -m] [<FILE>...]
  tweezer convert [<FILE>...] <LANGUAGE>
  tweezer overview [-t | -m] ([<DIR>...] | -f [<FILE>...])
  tweezer list [<DIR>...] [--kind=<TYPE>]
  tweezer show <OBJECT> [--kind=<TYPE>] [-d]
  tweezer update <OBJECT> [--kind=<TYPE>]
  tweezer track [-o <OBJECT>] ([<VIDEO>...] | -i [<IMAGE>...])
  tweezer simulate <OBJECT> [--args=<ARGS>...]
  tweezer plot <OBJECT> [--args=<ARGS>...]
  tweezer calculate <OBJECT> [--args=<ARGS>...]...
  tweezer help [<COMMAND>]
  tweezer (-h | --help)
  tweezer (-v | --version)

Commands:
  watch         Monitor directory for changes
  analyse       Perform specified data analysis
  analyze       Perform specified data analysis
  convert       Convert data to be able to work in specified language
  overview      Produce "Overview.pdf" for data files in directory
  list          List all files and file types in a directory recursively
  show          Shows content of an object or file in an informative way
  update        Update the object in question (mainly used for settings)
  track         Find position of features in images or videos
  simulate      Run simulation of type "object"
  plot          Plot examples and objects
  calculate     Perform calculations on the command line
  help          Show detailed help for a command or these help pages
Arguments:
  FILE          Input file
  PATH          Out directory
  DIR           Input directory
  LANGUAGE      Preferred language or data container
  OBJECT        Either general tweezer object (like settings) or concrete file
  TYPE          Generic classifier for general purposes
  IMAGE         Image file (.png, or .jpg)
  VIDEO         Video file (.avi, or .fits)
  ARGS          Keyword arguments (like n=4 p='test'); no spaces around "="
  COMMAND       Command name out of the list of commands

Options:
  -h --help         Show this screen
  -v --version      Show version number
  -t --tweebot      Tweebot tweezer mode
  -m --manual       Manual tweezer mode
  -l --logging      Write log file
  -k --kind=<TYPE>  Kind, type, part or subclass of an object
  -d --default      Refer to the saved default object
  -f --file         Switch to file mode when input can be file or dir
  -i --image        Switch to image mode when input can be image or video
  -a --args=<ARGS>  Additional keyword arguments to be passed to the command
"""
import os
import sys
import shutil

from docopt import docopt
from clint.textui import colored, puts, indent

from tweezer import __version__
try:
    from tweezer.cli.help import show_tweezer_help_pages

    from tweezer.cli.help import (print_plot_help, print_simulate_help,
                                  print_update_help,
                                  print_track_help, print_show_help,
                                  print_list_help, print_analyse_help)

    from tweezer.core.watcher import run_watcher
    from tweezer.cli.utils import list_tweezer_files
    from tweezer.cli import InterpretUserInput
    from tweezer.cli.utils import pprint_settings, update_settings
    from tweezer import _DEFAULT_SETTINGS
    from tweezer import _TWEEBOT_CONFIG
    from tweezer.ixo.json_ import parse_json

    from tweezer.simulate.brownian_motion import (
        simulate_naive_1D_brownian_motion)

    from tweezer.ixo.functions import get_function_arguments

    from tweezer.cli.plots import (matplotlib_example,
                                   plot_extensible_worm_like_chain)
    from tweezer.cli.calculations import calc_example, calc_viscosity

except ImportError, err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
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
        show_tweezer_help_pages()

    # Checking and setting default values
    if not args['--tweebot'] and not args['--manual']:
        args['--tweebot'] = True

    # check directory
    if not args['<DIR>']:
        args['<DIR>'] = os.getcwd()

    DIR = args['<DIR>']

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

        with indent(2):
            puts('Calling tweezer watch from {}\n'.format(colored.green(DIR)))
            puts('To stop this script hit {}.'.format(colored.red("CTRL + C")))

        run_watcher(DIR)

    # tweezer list
    if args['list']:

        puts('Calling tweezer list from {}'.format(colored.green(DIR)))
        files = list_tweezer_files(DIR)
        print('There are {} file types'.format(len(files)))
        print('There are the following types: {} '.format(len(files)))
        puts('Here is the result: ')

        for key, val in files.iteritems():
            if not 'directory_state' in key:
                with indent(2):
                    puts('These are the files of type {}:'.format(colored.yellow(key)))
                    puts('')
                    for v in val:
                        with indent(2):
                            if DIR in v:
                                puts('{}'.format(v.replace(DIR, '...')))
                            else:
                                puts('{}'.format(v))
            else:
                with indent(2):
                    puts('The {} is described by:'.format(colored.yellow('directory_state')))
                    puts('')
                    with indent(2):
                        puts('{}'.format(files['directory_state']))
            puts('')

    # tweezer show
    if args['show']:

        if args['--kind']:
            kind = args['--kind']
        else:
            kind = 'all'

        # Check objects with special meaning
        if 'setting' in args['<OBJECT>']:

            has_settings = os.path.isfile('settings.json')

            if has_settings:

                settings = parse_json('settings.json')

                if not args['--default']:
                    pprint_settings(settings, part=kind, status='local')

                else:
                    default_settings = parse_json(_DEFAULT_SETTINGS)
                    pprint_settings(default_settings, part=kind, 
                        status='default', other_settings=settings, other_status='locally')

            elif args['--default']:
                default_settings = parse_json(_DEFAULT_SETTINGS)
                if has_settings:
                    settings = parse_json('settings.json')
                    pprint_settings(default_settings, part=kind, 
                        status='default', other_settings=settings, other_status='locally')
                else:
                    pprint_settings(default_settings, part=kind, status='default')
            else:
                puts('No settings file found...\n')
                putSettigns = raw_input('Shall I add the default settings file to this directory: ')
                if InterpretUserInput[putSettigns]:
                    print('I am copying it over...')
                    shutil.copy2(_DEFAULT_SETTINGS, os.path.join(DIR, 'settings.json'))
                else:
                    print('Ok, than I have nothing to show...')

        elif 'result' in args['<OBJECT>']:
            print('These are the results:')

        elif 'tweebot' in args['<OBJECT>'] or 'configuration' in args['<OBJECT>']:

            has_tweebot_configs = os.path.isfile('tweebot_configuration.json')

            if has_tweebot_configs:

                if not args['--default']:
                    settings = parse_json('tweebot_configuration.json')
                    pprint_settings(settings, part=kind, status='local')
                else:
                    puts('These are the tweebot default configurations:\n')
                    settings = parse_json(_TWEEBOT_CONFIG)
                    pprint_settings(settings, part=kind, status='default')

            elif args['--default']:
                puts('These are the tweebot default configurations:\n')
                settings = parse_json(_TWEEBOT_CONFIG)
                pprint_settings(settings, part=kind, status='default')

            else:
                puts('No tweebot configuration file found...\n')
                putSettigns = raw_input('Shall I add the default tweebot configuration file to this directory: ')
                if InterpretUserInput[putSettigns]:
                    print('I am copying it over...')
                    shutil.copy2(_TWEEBOT_CONFIG, os.path.join(DIR, 'tweebot_configuration.json'))
                else:
                    print('Ok, than I have nothing to show...')

        elif 'files' in args['<OBJECT>']:

            CACHED_FILES = 'cached_file_listing.json'

            has_cached_file_listing = os.path.isfile(CACHED_FILES)

            if has_cached_file_listing:
                files = parse_json(CACHED_FILES)

                if kind is 'all':
                    for key, val in files.iteritems():
                        if not 'directory_state' in key:
                            with indent(2):
                                puts('These are the files of type {}:'.format(colored.yellow(key)))
                                puts('') 
                                for v in val:
                                    with indent(2):
                                        if DIR in v:
                                            puts('{}'.format(v.replace(DIR, '...')))
                                        else:
                                            puts('{}'.format(v))
                        else:
                            with indent(2):
                                puts('The {} is described by:'.format(colored.yellow('directory_state')))
                                puts('')
                                with indent(2):
                                    puts('{}'.format(files['directory_state']))
                        puts('')

                else:
                    try:
                        if kind not in ['directory_state', 'state']:
                            with indent(2):
                                puts('These are the files of type {}:'.format(colored.yellow(kind)))
                                puts('') 
                                for v in files[kind]: 
                                    with indent(2):
                                        if DIR in v:
                                            puts('{}'.format(v.replace(DIR, '...'))) 
                                        else:
                                            puts('{}'.format(v)) 
                        else:
                            with indent(2):
                                puts('The {} is described by:'.format(colored.yellow('directory_state')))
                                puts('') 
                                with indent(2):
                                    puts('{}'.format(files['directory_state']))
                        puts('') 
                    except KeyError:
                        print('No such file type found')

            else:
                puts('No files listing found...\n')
                putSettigns = raw_input('Shall I search the current directory for known file types: ')
                if InterpretUserInput[putSettigns]:
                    print("I'm classifying the files here. Might take a minute...")
                    files = list_tweezer_files(DIR)
                else:
                    print('Ok, than I have nothing to show...')

        else:
            print('This is the content of file {}'.format(args['<OBJECT>']))

    # tweezer update <OBJECT> [--kind=<TYPE>]
    if args['update']:

        if args['--kind']:
            kind = args['--kind']
        else:
            kind = 'all'

        # check special objects
        if 'setting' in args['<OBJECT>']:

            has_settings = os.path.isfile('settings.json')

            if has_settings:

                old_settings = parse_json('settings.json')

                update_settings('settings.json', old_settings=old_settings, part=kind)                

                # new_settings = parse_json('settings.json')

                default_settings = parse_json(_DEFAULT_SETTINGS)

                pprint_settings(old_settings, part=kind, other_settings=default_settings)

            else:
                puts('Update only works with local settings file, but none was found...\n')
                putSettigns = raw_input('Shall I add the default settings file to this directory: ')
                if InterpretUserInput[putSettigns]:
                    print('I am copying it over...')
                    shutil.copy2(_DEFAULT_SETTINGS, os.path.join(DIR, 'settings.json'))
                else:
                    print('Sorry, could not interpret your answer. Try (y | n)...')

        elif 'result' in args['<OBJECT>']:
            print('These are the results:')

        elif 'tweebot' in args['<OBJECT>'] or 'configuration' in args['<OBJECT>']:

            has_tweebot_configs = os.path.isfile('tweebot_configuration.json')

            if has_tweebot_configs:

                settings = parse_json('tweebot_configuration.json')

                pprint_settings(settings, part=kind)

            elif args['--default']:
                puts('These are the tweebot default configurations:\n')
                
                settings = parse_json(_TWEEBOT_CONFIG)

                pprint_settings(settings, part=kind, status='default')

            else:
                puts('No tweebot configuration file found...\n')
                putSettigns = raw_input('Shall I add the default tweebot configuration file to this directory: ')
                if InterpretUserInput[putSettigns]:
                    print('I am copying it over...')
                    shutil.copy2(_TWEEBOT_CONFIG, os.path.join(DIR, 'tweebot_configuration.json'))
                else:
                    print('Ok, than I have nothing to show...')

        else:
            print('This is the content of file {}'.format(args['<OBJECT>']))

    # tweezer simulate
    if args['simulate']:

        simulation_mapper = {'naive_brownian_motion': simulate_naive_1D_brownian_motion}

        try:
            sys.exit(simulation_mapper[args['<OBJECT>']](4, 100))
        except (KeyboardInterrupt, SystemExit), err:
            raise err
        except KeyError:
            with indent(2):
                puts('Could not find simulation {}\n'.format(colored.red(args['<OBJECT>'])))
                puts('Available simulations are: \n')
                for each in simulation_mapper:
                    args_list = get_function_arguments(simulation_mapper[each])
                    if args_list:
                        arg_string = ', '.join(args_list) 
                    else:
                        arg_string = ''
                    puts('{}({})\n'.format(colored.blue(each), colored.white(arg_string)))

    # tweezer plot
    if args['plot']:

        plot_mapper = {'matplotlib_example': matplotlib_example, 
            'wlc': plot_extensible_worm_like_chain,
            'eWLC': plot_extensible_worm_like_chain,
            'WLC': plot_extensible_worm_like_chain,
            'worm-like-chain': plot_extensible_worm_like_chain}

        try:
            sys.exit(plot_mapper[args['<OBJECT>']]())
        except (KeyboardInterrupt, SystemExit), err:
            raise err
        except KeyError:
            with indent(2):
                puts('Could not find plot routine for {}\n'.format(colored.red(args['<OBJECT>'])))
                puts('Available plotting examples are: \n')
                for each in plot_mapper:
                    args_list = get_function_arguments(plot_mapper[each])
                    if args_list:
                        arg_string = ', '.join(args_list) 
                    else:
                        arg_string = ''
                    puts('{}({})\n'.format(colored.blue(each), colored.white(arg_string)))


    # tweezer calculate
    if args['calculate']:

        calc_mapper = {'example': calc_example, 
                       'viscosity': calc_viscosity}

        try:
            if args['--args']:
                print(args['--args'])
                sys.exit(calc_mapper[args['<OBJECT>']]())
            else:
                sys.exit(calc_mapper[args['<OBJECT>']]())
        except (KeyboardInterrupt, SystemExit), err:
            raise err
        except KeyError:
            with indent(2):
                puts('Could not find calculation for {}\n'.format(colored.red(args['<OBJECT>'])))
                puts('Available calculations are: \n')
                for each in calc_mapper:
                    args_list = get_function_arguments(calc_mapper[each])
                    if args_list:
                        arg_string = ', '.join(args_list) 
                    else:
                        arg_string = ''
                    puts('{}({})\n'.format(colored.blue(each), colored.white(arg_string)))

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
                print(path)
                # tweebot_overview(path)

        puts('Calling {} from {}'.format(colored.white('tweezer overview'), colored.green(DIR)))
        # full_tweebot_overview(DIR)

    # tweezer help
    if args['help']:

        command = args['<COMMAND>']

        command_mapper = {'plot': print_plot_help, 
            'simulate': print_simulate_help, 'update': print_update_help, 
            'track': print_track_help, 'show': print_show_help, 
            'list': print_list_help, 'analyse': print_analyse_help}

        with indent(2):
            puts('Help pages for {} {} command:\n'.format(colored.green('tweezer'), colored.green(command)))

        if not command:
            show_tweezer_help_pages()
        else:
            try:
                command_mapper[command]()
            except:
                raise NotImplementedError('Still under construction')

