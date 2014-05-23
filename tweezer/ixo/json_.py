#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import re

try:
    import simplejson as json
except ImportError:
    import json

from tweezer.io import read_tweebot_data_header


def parse_json(fileName):
    """
    Parse a JSON file
    First remove comments and then use the json module package
    Comments look like :
        // ...
    or
        /*
        ...
        */

    Args:
        fileName (path): to json file

    Returns:
        content (dict): dictionary representing the JSON object
    """
    # Regular expression for comments
    comment_re = re.compile(
        '(^)?[^\S\n]*/(?:\*(.*?)\*/[^\S\n]*|/[^\n]*)($)?',
        re.DOTALL | re.MULTILINE
    )
    with open(fileName) as f:
        content = ''.join(f.readlines())

        ## Looking for comments
        match = comment_re.search(content)
        while match:
            # single line comment
            content = content[:match.start()] + content[match.end():]
            match = comment_re.search(content)

        # Return json file
        return json.loads(content)


def calibration_to_json(fileName):
    """
    Reads calibration data and returns them as a json object.

    Args:
        fileName (str): Path to a tweezer data file containing the calibration data as a header

    Returns:
        asJSON (str): JSON representation of calibration data.
    """
    headerInfo = read_tweebot_data_header(fileName)

    metaData = headerInfo.metadata

    for key, value in metaData.items():
        try:
            json.dumps(metaData[key])
        except TypeError:
            metaData[key] = str(value)

    units = headerInfo.units

    for key, value in units.items():
        try:
            json.dumps(units[key])
        except TypeError:
            units[key] = str(value)

    dictRepresentation = dict(metaData = metaData, units = units)

    try:
        asJSON = json.dumps(dictRepresentation)
    except TypeError as te:
        raise te

    return asJSON

