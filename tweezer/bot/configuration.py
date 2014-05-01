#!/usr/bin/env python
#-*- coding: utf-8 -*-

import re
from collections import OrderedDict, namedtuple

import numpy as np


def parse_tweebot_configuration_file(file_name='default.config.txt'):
    """
    Extracts configuration data from Tweebot Config File

    :param file_name: (path) to tweebot configuration file

    :return TweebotConfigData: (namedtuple) with configuration values and units as OrderedDicts
    """

    with open(file_name, 'r') as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines if l.strip()]

    comments = [(i, l.strip('//').strip()) for i, l in enumerate(lines) if l.strip().startswith('/')]
    raw = [(i, l.replace('\t','').replace(' ', '')) for i, l in enumerate(lines) if '=' in l and not l.strip().startswith('/')]

    values = OrderedDict()
    units = OrderedDict()

    for l in raw:
        parts = l[1].split('=')
        values[parts[0]] = parts[1]
        if len(parts) > 2:
            units[parts[0]] = parts[2]

    for key, val in values.iteritems():
        if re.search('^(\d|-\d)', str(val)):
            if '.' in str(val):
                val = round(np.float64(val), 12)
            elif 'e' in str(val):
                val = round(np.float64(val), 12)
            else:
                val = int(val)
            values[key] = val

    TweebotConfigData = namedtuple('TweebotConfigData', ['values', 'units', 'comments', 'raw', 'lines'])

    TweebotConfigData = TweebotConfigData(values, units, comments, raw, lines)

    return TweebotConfigData

