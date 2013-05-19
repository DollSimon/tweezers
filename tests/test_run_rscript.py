#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest
import sure
import nose
from nose.tools import with_setup
import pytest

import os
import envoy

def get_script():
    r_path = '/Library/Frameworks/R.framework/Resources/library/tweezR'
    r_file = 'tweebot_overviews.r'
    r_script = os.path.join(r_path, r_file)
    return r_script

def test_simple_rscript():
    r_script = get_script()
    
    # calling envoy
    r = envoy.run('echo {}'.format(r_script))
    r.status_code.should.equal(0) 
    r.std_out.rstrip().should.equal(r_script) 

    # calling tweebot script with no arguments
    t = envoy.run('Rscript {}'.format(r_script))
    t.status_code.should.equal(0) 
    
    # calling tweebot script with one arguments
    t = envoy.run('Rscript {} 4 x:n=5'.format(r_script))
    t.status_code.should.equal(0) 
  
