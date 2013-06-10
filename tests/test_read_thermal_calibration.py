#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest
import sure

from tweezer import path_to_sample_data

TS = path_to_sample_data('TC_TS')
PSD = path_to_sample_data('TC_PSD')


# Testing the test
def main():
    print(TS)
    print(PSD)

if __name__ == '__main__':
    main()
