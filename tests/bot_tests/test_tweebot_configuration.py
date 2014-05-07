#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sure
import unittest

from tweezer.bot.configuration import parse_tweebot_configuration_file 

from tweezer import _TWEEBOT_CONFIG_TXT

def test_parsing_of_tweebot_configuration():
    conf = parse_tweebot_configuration_file(_TWEEBOT_CONFIG_TXT)
