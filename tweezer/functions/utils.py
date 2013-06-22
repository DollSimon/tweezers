#!/usr/bin/env python
#-*- coding: utf-8 -*-

import inspect

def get_function_arguments(function):
    """
    Gets the arguments of a function definition as a list
    
    :param function: (function) 

    :return arguments: (list of str) list of function arguments
    """
    A = inspect.getargspec(function)
    arguments = []
    if A.defaults:
        no_defaults, with_defaults = A.args[:len(A.args)-len(A.defaults)], A.args[-len(A.defaults):]
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
    
