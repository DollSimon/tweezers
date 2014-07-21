#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
Routines related to producing experimental overview files
"""
import os

from clint.textui import colored, puts, indent


def full_tweebot_overview(path):
    print('Hurray')


def generate_tweebot_overview(data_file):
    """
    Top level routine for producing Tweebot overviews.

    :param data_file: (Path) to Tweebot datalog file
    """
    puts('Generating overview for: \n')
    with indent(2):
        puts('{}\n'.format(colored.red(data_file)))


def main():
    print('I am in tweezer.cli.overview')


if __name__ == '__main__':
    main()
