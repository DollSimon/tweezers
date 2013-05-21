#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
from clint.textui import colored, puts, indent 
from termcolor import cprint

from macropy.macros.adt import macros, case

from tweezer.core.parsers import classify


def list_tweezer_files(directory):
    """ 
    Walks a directory structure top-down, registering known tweezer file types along the way. 

    :param directory: (Path) starting directory

    
    """
    for (path, dirs, files) in os.walk(directory):
        with indent(2):
            puts("The current path is {}".format(colored.red(path)))
            with indent(2):
                puts("The dirs in the current level are {}".format(colored.blue(dirs)))
                with indent(2):
                    puts("The files in the current level are {}".format(colored.yellow(files)))

        puts("There are {} files.".format(colored.blue(sum(1 for f in files))))
        for f in files:
            print(classify(os.path.join(path, f)))


def file_cache(parameter):
    """
    Short description 

    :param parameter: Description

    :return name: Description
    """
    pass


@case 
class MyPoint(x, y): 
    def rocket(self, n):
        print(n)

@case 
class TweezerFile(file_type, date, origin):
    pass


def 
