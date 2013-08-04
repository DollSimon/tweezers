#!/usr/bin/env python
#-*- coding: utf-8 -*-

import cProfile

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
