#!/usr/bin/env python
#-*- coding: utf-8 -*-

from clint.textui import colored, puts, indent

from tweezer import __version__

VERSION = ".".join(str(x) for x in __version__)


def show_tweezer_help_pages():
    puts('{0} : {1}'.format(colored.blue('tweezer'), 'A data analysis tool for single-molecule experiments'))
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
            puts('tweezer show <OBJECT> [--part=<TYPE>] [-d]')
            puts('tweezer update <OBJECT> [--part=<TYPE>]')
            puts('tweezer track [-o <OBJECT>] ([<VIDEO>...] | -i [<IMAGE>...])')
            puts('tweezer simulate <OBJECT> [--args=<ARGS>...]')
            puts('tweezer plot <OBJECT> [--args=<ARGS>...]')
            puts('tweezer calculate <OBJECT> [-c] [-h] [--args=<ARGS>...]...')
            puts('tweezer help [<COMMAND>]')
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
            puts('show          Shows content of an object or file in an informative way')
            puts('update        Updates the object in question (mainly used for settings)')
            puts('calculate     Perform calculations on the command line')
            puts('track         Find position of features in images or videos')
            puts('simulate      Run simulation of type "object"')
            puts('plot          Plot examples and objects')
            puts('help          Show detailed help for a command or these help pages')

        puts('\n{}:'.format(colored.green('Arguments')))
        with indent(2):
            puts('FILE          Input file')
            puts('PATH          Out directory')
            puts('DIR           Input directory')
            puts('LANGUAGE      Preferred language or data container')
            puts('OBJECT        Either general tweezer object (like settings) or concrete file')
            puts('IMAGE         Image file (.png, or .jpg)')
            puts('VIDEO         Video file (.avi, or .fits)')
            puts('ARGS          Keyword arguments (like n=4 p="test"); no spaces around "="')
            puts('COMMAND       Command name out of the list of commands')

        puts('\n{}:'.format(colored.green('Options')))
        with indent(2):
            puts('-h --help         Show this screen')
            puts('-v --version      Show version number')
            puts('-t --tweebot      Tweebot tweezer mode')
            puts('-m --manual       Manual tweezer mode')
            puts('-l --logging      Write log file')
            puts('-p --part=<TYPE>  Part or Subclass of an object')
            puts('-d --default      Refer to the saved default object')
            puts('-f --file         Switch to file mode when input can be file or dir')
            puts('-i --image        Switch to image mode when input can be image or video')
            puts('-a --args=<ARGS>  Additional keyword arguments to be passed to the command')
            puts('-c --clean        Suppress terminal output of extra information')


def print_plot_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer plot')))


def print_overview_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer overview')))

def print_simulate_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer simulate')))


def print_show_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer show')))


def print_analyse_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer analyse')))


def print_watch_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer watch')))


def print_track_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer track')))


def print_update_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer update')))


def print_list_help():
    with indent(2):
        puts('Help for {} command:\n'.format(colored.white('tweezer list')))


def main():
    show_tweezer_help_pages()

if __name__ == '__main__':
    main()
