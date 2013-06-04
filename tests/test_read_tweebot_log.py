#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import unittest
import sure

from tweezer.io import read_tweebot_logs
from tweezer.core.parsers import classify

_ROOT = os.path.abspath(os.path.dirname(__file__))
LOGFILE = os.path.join(os.path.dirname(_ROOT), 
    'tweezer', 'data', 'bot_logs', '32.TweeBotLog.2013.05.19.01.50.21.txt')

def test_correct_file_type():
    classify(LOGFILE).should.equal('BOT_LOG') 
    

def test_read_tweebot_log_opens_file():
    log = read_tweebot_logs(LOGFILE)
    len(log.index).should.equal(1042) 


def main():
    print(_ROOT)
    print(LOGFILE)

if __name__ == '__main__':
    main()

