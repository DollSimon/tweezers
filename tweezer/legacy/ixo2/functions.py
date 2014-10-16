#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import inspect


def get_function_arguments_as_string(function):
    """
    Gets the arguments of a function definition as a list

    :param function: (function)

    :return arguments: (list of str) list of function arguments
    """
    A = inspect.getargspec(function)
    arguments = []
    if A.defaults:
        no_defaults = A.args[:len(A.args) - len(A.defaults)]
        with_defaults = A.args[-len(A.defaults):]
    else:
        no_defaults, with_defaults = A.args, None
    if no_defaults:
        for each in no_defaults:
            arguments.append(each)
    if with_defaults:
        for i, a in enumerate(with_defaults):
            arguments.append('='.join([a, str(A.defaults[i])]))
    if A.varargs:
        arguments.append('*' + A.varargs)
    if A.keywords:
        arguments.append('**' + A.keywords)
    return arguments


def get_function_arguments(function):
    """
    Gets the arguments of a function definition as a dictionary

    :param function: (function)

    :return arguments: (dict) dictionary of function arguments
    """
    A = inspect.getargspec(function)
    arguments = {}
    if A.defaults:
        no_defaults = A.args[:len(A.args) - len(A.defaults)]
        with_defaults = A.args[-len(A.defaults):]
    else:
        no_defaults, with_defaults = A.args, None
    if no_defaults:
        arguments['noDefault'] = no_defaults
    if with_defaults:
        for i, a in enumerate(with_defaults):
            arguments[a] = A.defaults[i]
    if A.varargs:
        arguments['varArgs'] = A.varargs
    if A.keywords:
        arguments['keywords'] = A.keywords
    return arguments


def build_argument_string(func):
    """
    Building the argument string for printing
    """
    argString = "(" + ", ".join(get_function_arguments_as_string(func)) + ")"
    return argString


def main():
    def my_func(water, n=4, m='trial', *nim, **trim):
        return n
    args = get_function_arguments(my_func)
    print(args)
    # print(my_func(5, **args))

if __name__ == '__main__':
    sys.exit(main())
