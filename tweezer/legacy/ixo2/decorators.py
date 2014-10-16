#!/usr/bin/env python
#-*- coding: utf-8 -*-

import cProfile
import time
import types

from functools import wraps

from nose.plugins.attrib import attr
from nose.plugins.skip import SkipTest


###############################################################################
## Decorators for Profiling and Logging functions
###############################################################################
def profile_this(fn):
    """
    Decorator to profile the execution time of a function

    :param fn: function to be profiled
    """
    def profiled_fn(*args, **kwargs):
        # name of profile dump
        fpath = fn.__name__ + ".profile"
        prof = cProfile.Profile()
        ret = prof.runcall(fn, *args, **kwargs)
        prof.dump_stats(fpath)
        return ret
    return profiled_fn


def time_this(fn):
    """
    Decorator that reports the execution time.

    Ref: Python Cookbook 3, 9.5
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        end = time.time()
        print("Execution time for {}: {} s".format(fn.__name__, end - start))
        return result
    return wrapper


###############################################################################
## Decorators as classes
###############################################################################
class TerminalInfoSwitch(object):
    """Switch to turn on or off informative output when a function is called in
    the terminal"""
    def __init__(self, showInfos=False):
        self.showInfos = showInfos


def informative(terminalInfoSwitch):
    """
    Add informative output to a function call.

    This is a decorator factory. It returns a decorator. The behaviour of the \
    decorated function can be changed by changing the properties of the \
    *terminalInfoSwitch* instance. This can be done at run-time.

    Usage:
    >>> tis = TerminalInfoSwitch()
    >>> @informative(tis)
    ... def fn(x=4, y=7):
    ...     return x + y
    >>>
    >>> fn()
    >>> tis.showInfos = False
    >>> fn()
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if terminalInfoSwitch.showInfos:
                print("I'm showing the information for function {}".format(fn))
            else:
                print("Showing nothing")
            result = fn(*args, **kwargs)
            return result
        return wrapper
    return decorator


class TerminalInformation:
    """
    Decorator class that allows you to change the way a function is called at \
    run-time.

    Adjusted for Python 2.7 from Python Cookbook 3, 9.9


    If combined with other decorators, use as the outermost one.

    Usage:
    >>> @TerminalInformation
    ... def fn(x=4, y=7):
    ...     return x + y
    >>>
    >>> fn()
    >>> fn.showInfos = True
    >>> fn()
    """
    def __init__(self, fn, showInfos=True):
        wraps(fn)(self)
        self.fn = fn
        self.ncalls = 0
        self.showInfos = showInfos

    def __call__(self, *args, **kwargs):
        self.ncalls += 1
        if self.showInfos:
            print("Function name is {}".format(self.fn.__name__))
            print("Boooh")
        else:
            print('hurray')
        return self.fn(*args, **kwargs)

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            return types.MethodType(self, instance)


###############################################################################
## Decorators for testing, TDD and BDD
###############################################################################
def fail(message):
    raise AssertionError(message)


def wip(f):
    @wraps(f)
    def run_test(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except Exception as e:
            raise SkipTest("WIP test failed: " + str(e))
        fail("test passed but marked as work in progress")

    return attr('wip')(run_test)


def main():

    @TerminalInformation
    def fn1(x=4, y=5):
        """
        This is my function
        """
        z = x * y
        print("z = {}".format(z))
        return z

    fn1()
    fn1()
    fn1.showInfos = True
    fn1(3, 4.3)
    print(fn1.ncalls)


if __name__ == '__main__':
    main()
