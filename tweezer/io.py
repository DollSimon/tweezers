"""
Input/Output routines for the tweezer package.

Performs file reads and data conversion.
"""


def txt_reader(filename):
    """
    Reads dual-trap data and metadata contained in text files
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    return lines


def tweebot_txt_reader(filename):
    """
    Reads dual-trap data and metadata from TweeBot text files
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

    return lines


def mat_reader(filename):
    """
    Reads data from Matlab file
    """
    pass
