#!/usr/bin/env python

from pymongo import Connection
from pathlib import Path


def main():
    # get all data files

    p = Path('.')

    files = p.glob('**/data/*.txt')

    for f in files:
        fileName = f.absolute().as_posix()
        headerInfo = read_tweebot_data_header(fileName)

    c = Connection()
    db = c.calibration



