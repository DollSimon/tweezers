#! /usr/bin/env python

"""
Tweezer Data Analysis

Usage:
  tweeze.py overview <dir>...
  tweeze.py analyse <dir> [--speed=<kn>]
  tweeze.py analyze <name> move <x> <y> [--speed=<kn>]
  tweeze.py watch <dir>
  tweeze.py (-h | --help)
  tweeze.py --version

Options:
  -h --help             Show this screen.
  --version             Show version.
  --operator=<mode>     Who runs the tweezer (tweebot / manual)? [default: tweebot]
"""
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Tweezer Data Analysis 0.1')
    print("rocket")
    print(arguments)