"""
Import routines for tweezer data from different sources.
"""

from pathlib import Path
import re
from collections import OrderedDict
import json

import pandas as pd
import numpy as np

from .tweezer.legacy.io.helper import *


def read_mpi_data(fileName):
    """
    Import a txt data file from tweezer experiments at the MPI-CBG with the JSON header format.

    Args:
        fileName (pathlib.Path or str): full path to the txt data file

    Returns:

    """

    # convert fileName to Path object if it is a string
    if type(fileName) is str:
        fileName = Path(fileName)

    if not fileName.exists() or not fileName.is_file():
        raise FileExistsError

    with fileName.open() as f:
        # read header lines
        jsonHeader = ''
        line = f.readline()
        nLines = 1
        while line != '#### DATA ####\n':
            jsonHeader += line
            line = f.readline()
            nLines += 1

        # get column header row
        line = f.readline().strip()
        while not line:
            line = f.readline().strip()
            nLines += 1
        columnTitles = line

    # convert JSON header to OrderedDict
    meta = json.loads(jsonHeader, object_pairs_hook=OrderedDict)

    # get column headers
    regex = re.compile('(\w*) \(([^)]*)\)')
    res = regex.findall(columnTitles)
    units = {column: unit for (column, unit) in res}
    columns = [title[0] for title in res]

    # read data
    data = pd.read_table(fileName.__str__(), sep='\t', header=None, skiprows=nLines + 1,
            names=columns, dtype=np.float64)

    # drop rows with "NaN" values
    data = data.dropna()

    # creating index
    time = pd.Series(meta['timeStep'] * np.array(range(0, len(data))))
    data['time'] = time
    data.set_index('time', inplace=True)

    # adding attributes
    data.units = units
    data.meta = meta

    return data


def read_mpi_data_old(fileName):
    """
    Import a txt data file from tweezer experiments at the MPI-CBG with the old comment-style header format.

    Args:
        fileName (pathlib.Path or str): full path to the txt data file

    Returns:

    """

    # convert fileName to Path object if it is a string
    if type(fileName) is str:
        fileName = Path(fileName)

    if not fileName.exists() or not fileName.is_file():
        raise FileExistsError

    # read all the header lines and count them
    with fileName.open() as f:
        commentLines = []
        # this array holds the line numbers of all non-data lines, this is required for a sanity check
        # that looks at the last line in the file and checks if it is a data line or not
        nonDataLines = []
        nLine = 0
        # use a generator to not store all the lines already
        lines = (line.strip() for line in f)
        for line in lines:
            if not line or not line.startswith(tuple('-0123456789')):
                nonDataLines.append(nLine)
                if line.startswith('#'):
                    # check for config line
                    commentLines.append(line)
                elif line and line[0].isalnum():
                    # the only line starting with a character is the column-title line
                    columnTitles = line
            nLine += 1

    # get default metadata structure
    meta = get_default_metadata()

    # get metadata from header lines, use regular expression
    # line has to start with '#', matches are named
    regex = re.compile('^# (?P<name>[^(:]*)\s?(\((?P<unit>[^:]*)\))?\s?:\s?(?P<value>.*)')
    for line in commentLines:
        res = regex.search(line)
        # check if a valid header line is found
        if not res:
            print('Empty header line? ' + line)
            continue
        if res.group('name') is None or res.group('value') is None:
            print('Info: Header conversion: Could not detect header data in line:' + line)
            continue

        # get the universal identifier for the header line
        key = get_standard_identifier(res.group('name'))
        # get the "key-path" where the value should be stored in the metadata dictionary
        metaKey = get_meta_key(key)
        # convert the value from string to its correct format
        value = convert_value_type(key, res.group('value'))

        # insert the key/value and the unit if available
        meta_insert_from_key(meta, metaKey, value)
        if res.group('unit') is not None:
            meta_insert_from_key(meta, get_meta_key(key + 'Unit'), res.group('unit'))

    # check file sanity: sometimes header lines end up at the end of the data file
    # normally the last line should be a data line
    meta['isFileSane'] = not nLine-1 == nonDataLines[-1]
    # store original file name
    meta['originalFile'] = fileName.name

    # read column titles and units
    regex = re.compile('(\w*) \(([^)]*)\)')
    res = regex.findall(columnTitles)
    units = {column: unit for (column, unit) in res}
    columns = [title[0] for title in res]

    # read data into pandas.DataFrame
    data = pd.read_table(fileName.__str__(), sep='\t', header=None, skiprows=nonDataLines,
            names=columns, dtype=np.float64)

    # drop rows with "NaN" values
    data = data.dropna()

    # creating index
    time = pd.Series(meta['timeStep'] * np.array(range(0, len(data))))
    data['time'] = time
    data.set_index('time', inplace=True)

    # adding attributes
    data.units = units
    data.meta = meta

    return data


def get_default_metadata():
    """
    Returns the default header information. Use this to make sure the metadata dictionary contains certain
    entries. But keep in mind that as many entries as possible should be optional and don't require a default.

    Returns:

    """

    meta = OrderedDict()
    return meta


