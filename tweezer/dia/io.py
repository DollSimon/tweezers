#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

from itertools import chain
from collections import namedtuple

from datetime import datetime

import numpy as np
import pandas as pd


def read_image(file_name):
    pass


def read_andor_fits_stack(file_name):
    pass


def read_tweezer_avi(file_name):
    pass


def read_distance_calibration_results(file_name):
    """
    Reads distance calibration results

    :param file_name: (path) to the distance calibration file
    
    """
    trap = 'pm' if 'pm' in os.path.basename(file_name).lower() else 'aod'

    with open(file_name, 'r') as f:
        lines = [l.strip().strip('#').strip() for l in f.readlines()] 
        lines = [l for l in lines] 


    units = {}
    data = {}

    for line in lines:
        if 'Date' in line:
            date_string = line.split(": ")[-1].replace("\t", " ")
        elif '2Pixel X (Hz/px)' in line:
            try:
                xConversionFactor = float(line.strip().split(": ")[-1]) 
            except:
                xConversionFactor = None

            data['xConversionFactor'] = xConversionFactor
            units['xConversionFactor'] = 'px/Hz'

        elif '2Pixel X (V/px)' in line:
            try:
                xConversionFactor = float(line.strip().split(": ")[-1]) 
            except:
                xConversionFactor = None

            data['xConversionFactor'] = xConversionFactor
            units['xConversionFactor'] = 'px/V'

        elif '2Pixel Y (Hz/px)' in line:
            try:
                yConversionFactor = float(line.strip().split(": ")[-1]) 
            except:
                yConversionFactor = None

            data['yConversionFactor'] = yConversionFactor
            units['yConversionFactor'] = 'px/Hz'

        elif '2Pixel Y (V/px)' in line:
            try:
                yConversionFactor = float(line.strip().split(": ")[-1]) 
            except:
                yConversionFactor = None

            data['yConversionFactor'] = yConversionFactor
            units['yConversionFactor'] = 'px/V'

        elif 'Intercept X' in line:
            try:
                xIntercept = float(line.strip().split(": ")[-1]) 
            except:
                xIntercept = None

            data['xIntercept'] = xIntercept
            units['xIntercept'] = 'px'

        elif 'Intercept Y' in line:
            try:
                yIntercept = float(line.strip().split(": ")[-1]) 
            except:
                yIntercept = None

            data['yIntercept'] = yIntercept
            units['yIntercept'] = 'px'

        elif 'STD X' in line:
            try:
                xStd = float(line.strip().split(": ")[-1]) 
            except:
                xStd = None

            data['xStd'] = xStd
            if 'aod' in trap:
                units['xStd'] = 'px/Hz'
            elif 'pm' in trap:
                units['xStd'] = 'px/V'

        elif 'STD Y' in line:
            try:
                yStd = float(line.strip().split(": ")[-1]) 
            except:
                yStd = None

            data['yStd'] = yStd
            if 'aod' in trap:
                units['xStd'] = 'px/Hz'
            elif 'pm' in trap:
                units['xStd'] = 'px/V'

    # parsing the date
    if date_string:
        date = datetime.strptime(date_string, '%m/%d/%Y %I:%M %p')
    else:
        date = datetime.now()

    DistanceCalibration = namedtuple('DistanceCalibrationResults', 
        ['trap', 'xConversionFactor', 'yConversionFactor',
        'xIntercept', 'yIntercept', 'xStd', 'yStd', 'date', 'units'])

    results = DistanceCalibration(trap, 
        data['xConversionFactor'], 
        data['yConversionFactor'], 
        data['xIntercept'], 
        data['yIntercept'], 
        data['xStd'], 
        data['yStd'], 
        date, units)

    return results


def read_distance_calibration_matrix(file_name):
    """
    Reads distance calibration matrix

    :param file_name: (path) to the distance calibration file 
    :param trap: (str) designating the trap of interest, either 'pm' or 'aod'
    """
    trap = 'pm' if 'pm' in os.path.basename(file_name).lower() else 'aod'

    with open(file_name, 'r') as f:
        lines = [l.strip().split('\t') for l in f.readlines()]
        lines = [l for l in lines if l]

    data = [l for l in lines if len(l) == max(len(l) for l in lines)]
    setup = [l for l in lines if len(l) == min(len(l) for l in lines)]

    setup = [float(s) for s in list(chain.from_iterable(setup))]

    # determine trap steps
    start = setup[0]
    step = setup[1]
    nStepsX = int(setup[2]) 
    nStepsY = int(setup[3]) 

    if nStepsX == nStepsY:
        xTrapPositions = yTrapPositions = [round(start + step * i, 6) for i in range(nStepsY)]
    else:
        xTrapPositions = [round(start + step * i, 6) for i in range(nStepsX)]
        yTrapPositions = [round(start + step * i, 6) for i in range(nStepsY)]

    xTemplatePositions = [d for d in data[1:nStepsX]]
    yTemplatePositions = [d for d in data[nStepsX:]]

    xArray = np.zeros((nStepsX, nStepsY))
    yArray = np.zeros((nStepsX, nStepsY))

    # filling arrays with positions
    for i, x in enumerate(xTemplatePositions):
        xArray[i] = x

    for j, y in enumerate(yTemplatePositions):
        yArray[j] = y

    xDF = pd.DataFrame(xArray, index=xTrapPositions, columns=yTrapPositions)
    yDF = pd.DataFrame(yArray, index=yTrapPositions, columns=xTrapPositions)

    # split data in the middle

    # create steps for the 
    DistanceCalibration = namedtuple('DistanceCalibrationMatrix', 
        ['trap', 'xDF', 'yDF']) 

    results = DistanceCalibration(trap, xDF, yDF)

    return results

