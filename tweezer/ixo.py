#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
General utility functions used for tweezer package.

"""
import os
import re
import cProfile
import datetime
import copy
from collections import namedtuple

import numpy as np
import envoy


def profile_this(fn):
    """
    Decorator to profile the execution time of a function

    :param fn: function to be profiled
    """
    def profiled_fn(*args, **kwargs):
        # name of profile dump
        fpath = fn.__name__ + ".profile"
        prof = cProfile.Profile()
        ret = prof.runcall(fn, *args, **kwargs)
        prof.dump_stats(fpath)
        return ret
    return profiled_fn


def get_subdirs(path, is_file=True):
    """
    Splits a path into its subdirectories and returns a list of those

    :param path: file path
    :param is_file: (Boolean) defaults to True for a complete file_name

    :return subdirs: List of subdirectories that make up a path
    """
    if is_file:
        _path = os.path.dirname(path)
    else:
        _path = path

    subdirs = []
    while True:
        _path, folder = os.path.split(_path)

        if folder!="":
            subdirs.append(folder)
        else:
            if _path!="":
                subdirs.append(_path)
            break

    subdirs.reverse()

    return subdirs


def get_parent_directory(file_name):
    """
    Extracts the parent directory of a file from an absolute path

    :param file_name: (Path)

    :return parent_dir: (String) name of parent directory
    """
    return get_subdirs(file_name)[-1]


def run_rscript(script, script_path='/Library/Frameworks/R.framework/Resources/library/tweezR/', **kwargs):
    """
    Calls an R script

    :param script: (Str) name of the script

    :param script_path: (Path)
    """
    if script_path[-1] == '/':
        path = "".join(script_path, script)
    else:
        path = "/".join(script_path, script)

    r = envoy.run("Rscript {} ")


def compile_pytex_file(pytex_file='pytex_template.tex'):
    """
    Compile a [PythonTex](https://github.com/gpoore/pythontex) file into

    :param pytex_file: (.tex file) A pytexDescription

    """
    pdflatex_call = envoy.run("pdflatex -interaction=batchmode {}".format(pytex_file))
    pytex_call = envoy.run("pythontex.py {}".format(pytex_file))
    pdflatex_call = envoy.run("pdflatex -interaction=batchmode {}".format(pytex_file))


class TweebotDictionary(namedtuple('TweebotDictionary', ['date', 
        'timeOfExperiment', 
        'laserDiodeTemp', 
        'laserDiodeHours',
        'laserDiodeCurrent',
        'andorAodCenterX',
        'andorAodCenterY',
        'andorAodRangeX',
        'andorAodRangeY',
        'ccdAodCenterX',
        'ccdAodCenterY',
        'ccdAodRangeX',
        'ccdAodRangeY',
        'andorPmCenterX',
        'andorPmCenterY',
        'andorPmRangeX',
        'andorPmRangeY',
        'ccdPmCenterX',
        'ccdPmCenterY',
        'ccdPmRangeX',
        'ccdPmRangeY',
        'andorPixelSizeX',
        'andorPixelSizeY',
        'ccdPixelSizeX',
        'ccdPixelSizeY',
        'aodDetectorOffsetX',
        'aodDetectorOffsetY',
        'aodStiffnessX',
        'aodStiffnessY',
        'aodDistanceConversionX',
        'aodDistanceConversionY',
        'pmDetectorOffsetX',
        'pmDetectorOffsetY',
        'pmStiffnessX',
        'pmStiffnessY',
        'pmDistanceConversionX',
        'pmDistanceConversionY',
        'aodBeadRadius',
        'pmBeadRadius',
        'samplingRate',
        'nSamples',
        'deltaTime',
        'timeStep'])):
    """
    TweebotDictionary is build on a namedtuple for easy access of variables with the dot notation.
    In addition to the namedtuple it allows for default values to be set and extra values to be added when needed.
    However, it preserves the immutability of the namedtuple on first glance. To set a value after initiation use
    d = d._replace(key=value)

    """
    def __new__(cls, date=None, 
        timeOfExperiment=None, 
        laserDiodeTemp=None, 
        laserDiodeHours=None,
        laserDiodeCurrent=None,
        andorAodCenterX=None,
        andorAodCenterY=None,
        andorAodRangeX=None,
        andorAodRangeY=None,
        ccdAodCenterX=None,
        ccdAodCenterY=None,
        ccdAodRangeX=None,
        ccdAodRangeY=None,
        andorPmCenterX=None,
        andorPmCenterY=None,
        andorPmRangeX=None,
        andorPmRangeY=None,
        ccdPmCenterX=None,
        ccdPmCenterY=None,
        ccdPmRangeX=None,
        ccdPmRangeY=None,
        andorPixelSizeX=None,
        andorPixelSizeY=None,
        ccdPixelSizeX=None,
        ccdPixelSizeY=None,
        aodDetectorOffsetX=None,
        aodDetectorOffsetY=None,
        aodStiffnessX=None,
        aodStiffnessY=None,
        aodDistanceConversionX=None,
        aodDistanceConversionY=None,
        pmDetectorOffsetX=None,
        pmDetectorOffsetY=None,
        pmStiffnessX=None,
        pmStiffnessY=None,
        pmDistanceConversionX=None,
        pmDistanceConversionY=None,
        aodBeadRadius=None,
        pmBeadRadius=None,
        samplingRate=None,
        nSamples=None,
        deltaTime=None,
        timeStep=None):
        # add default values
        return super(TweebotDictionary, cls).__new__(cls, date, 
        timeOfExperiment, 
        laserDiodeTemp, 
        laserDiodeHours,
        laserDiodeCurrent,
        andorAodCenterX,
        andorAodCenterY,
        andorAodRangeX,
        andorAodRangeY,
        ccdAodCenterX,
        ccdAodCenterY,
        ccdAodRangeX,
        ccdAodRangeY,
        andorPmCenterX,
        andorPmCenterY,
        andorPmRangeX,
        andorPmRangeY,
        ccdPmCenterX,
        ccdPmCenterY,
        ccdPmRangeX,
        ccdPmRangeY,
        andorPixelSizeX,
        andorPixelSizeY,
        ccdPixelSizeX,
        ccdPixelSizeY,
        aodDetectorOffsetX,
        aodDetectorOffsetY,
        aodStiffnessX,
        aodStiffnessY,
        aodDistanceConversionX,
        aodDistanceConversionY,
        pmDetectorOffsetX,
        pmDetectorOffsetY,
        pmStiffnessX,
        pmStiffnessY,
        pmDistanceConversionX,
        pmDistanceConversionY,
        aodBeadRadius,
        pmBeadRadius,
        samplingRate,
        nSamples,
        deltaTime,
        timeStep)


class TweezerUnits(TweebotDictionary):
        def __new__(cls, date=None, 
            timeOfExperiment=None, 
            laserDiodeTemp='C', 
            laserDiodeHours='h',
            laserDiodeCurrent='A',
            andorAodCenterX='px',
            andorAodCenterY='px',
            andorAodRangeX='px',
            andorAodRangeY='px',
            ccdAodCenterX='px',
            ccdAodCenterY='px',
            ccdAodRangeX='px',
            ccdAodRangeY='px',
            andorPmCenterX='px',
            andorPmCenterY='px',
            andorPmRangeX='px',
            andorPmRangeY='px',
            ccdPmCenterX='px',
            ccdPmCenterY='px',
            ccdPmRangeX='px',
            ccdPmRangeY='px',
            andorPixelSizeX='nm',
            andorPixelSizeY='nm',
            ccdPixelSizeX='nm',
            ccdPixelSizeY='nm',
            aodDetectorOffsetX='V',
            aodDetectorOffsetY='V',
            aodStiffnessX='pN/nm',
            aodStiffnessY='pN/nm',
            aodDistanceConversionX='V/nm',
            aodDistanceConversionY='V/nm',
            pmDetectorOffsetX='V',
            pmDetectorOffsetY='V',
            pmStiffnessX='pN/nm',
            pmStiffnessY='pN/nm',
            pmDistanceConversionX='V/nm',
            pmDistanceConversionY='V/nm',
            aodBeadRadius='nm',
            pmBeadRadius='nm',
            samplingRate='Hz',
            nSamples='int',
            deltaTime='s',
            timeStep='s'):
            # add default values
            return super(TweezerUnits, cls).__new__(cls, date, 
            timeOfExperiment, 
            laserDiodeTemp, 
            laserDiodeHours,
            laserDiodeCurrent,
            andorAodCenterX,
            andorAodCenterY,
            andorAodRangeX,
            andorAodRangeY,
            ccdAodCenterX,
            ccdAodCenterY,
            ccdAodRangeX,
            ccdAodRangeY,
            andorPmCenterX,
            andorPmCenterY,
            andorPmRangeX,
            andorPmRangeY,
            ccdPmCenterX,
            ccdPmCenterY,
            ccdPmRangeX,
            ccdPmRangeY,
            andorPixelSizeX,
            andorPixelSizeY,
            ccdPixelSizeX,
            ccdPixelSizeY,
            aodDetectorOffsetX,
            aodDetectorOffsetY,
            aodStiffnessX,
            aodStiffnessY,
            aodDistanceConversionX,
            aodDistanceConversionY,
            pmDetectorOffsetX,
            pmDetectorOffsetY,
            pmStiffnessX,
            pmStiffnessY,
            pmDistanceConversionX,
            pmDistanceConversionY,
            aodBeadRadius,
            pmBeadRadius,
            samplingRate,
            nSamples,
            deltaTime,
            timeStep)


def extract_meta_and_units(comment_list, file_type='man_data'):
    """
    Extracts metadata and units from the comments in raw tweezer data files

    :param comment_list: (list) List of strings that hold the raw comment lines

    :param file_type: (str) identifies the file type for which meta and units are extracted

    :return CommentInfo: (namedtuple) that holds dictionaries for metadata and units
    """
    units = {}
    meta = {}

    # set defaults
    units['laserDiodeCurrent'] = 'A'
    units['laserDiodeHours'] = 'h'
    units['laserDiodeTemp'] = 'C'
    units['viscosity'] = 'pN s / nm^2'

    units['samplingRate'] = 'Hz'
    units['recordingRate'] = 'Hz'
    units['timeStep'] = 's'

    units['aodDetectorOffsetX'] = 'V'
    units['aodDetectorOffsetY'] = 'V'
    units['pmDetectorOffsetX'] = 'V'
    units['pmDetectorOffsetY'] = 'V'

    units['pmDistanceConversionX'] = 'V/nm'
    units['pmDistanceConversionY'] = 'V/nm'
    units['aodDistanceConversionX'] = 'V/nm'
    units['aodDistanceConversionY'] = 'V/nm'

    units['pmDisplacementSensitivityX'] = 'V/nm'
    units['pmDisplacementSensitivityY'] = 'V/nm'
    units['aodDisplacementSensitivityX'] = 'V/nm'
    units['aodDisplacementSensitivityY'] = 'V/nm'

    units['pmStiffnessX'] = 'pN/nm'
    units['pmStiffnessY'] = 'pN/nm'
    units['aodStiffnessX'] = 'pN/nm'
    units['aodStiffnessY'] = 'pN/nm'

    units['pmBeadDiameter'] = 'nm'
    units['aodBeadDiameter'] = 'nm'
    units['pmBeadRadius'] = 'nm'
    units['aodBeadRadius'] = 'nm'

    units['laserDiodeTemp'] = 'C' 
    units['laserDiodeHours'] = 'h'
    units['laserDiodeCurrent'] = 'A'
    units['andorAodCenterX'] = 'px'
    units['andorAodCenterY'] = 'px'
    units['andorAodRangeX'] = 'px'
    units['andorAodRangeY'] = 'px'
    units['ccdAodCenterX'] = 'px'
    units['ccdAodCenterY'] = 'px'
    units['ccdAodRangeX'] = 'px'
    units['ccdAodRangeY'] = 'px'
    units['andorPmCenterX'] = 'px'
    units['andorPmCenterY'] = 'px'
    units['andorPmRangeX'] = 'px'
    units['andorPmRangeY'] = 'px'
    units['ccdPmCenterX'] = 'px'
    units['ccdPmCenterY'] = 'px'
    units['ccdPmRangeX'] = 'px'
    units['ccdPmRangeY'] = 'px'
    units['andorPixelSizeX'] = 'nm'
    units['andorPixelSizeY'] = 'nm'
    units['ccdPixelSizeX'] = 'nm'
    units['ccdPixelSizeY'] = 'nm'
    units['aodDetectorOffsetX'] = 'V'
    units['aodDetectorOffsetY'] = 'V'
    units['aodStiffnessX'] = 'pN/nm'
    units['aodStiffnessY'] = 'pN/nm'
    units['aodDistanceConversionX'] = 'V/nm'
    units['aodDistanceConversionY'] = 'V/nm'
    units['pmDetectorOffsetX'] = 'V'
    units['pmDetectorOffsetY'] = 'V'
    units['pmStiffnessX'] = 'pN/nm'
    units['pmStiffnessY'] = 'pN/nm'
    units['pmDistanceConversionX'] = 'V/nm'
    units['pmDistanceConversionY'] = 'V/nm'
    units['aodBeadRadius'] = 'nm'
    units['pmBeadRadius'] = 'nm'
    units['samplingRate'] = 'Hz'
    units['nSamples'] = 'int'
    units['deltaTime'] = 's'

    meta['laserDiodeCurrent'] = None
    meta['laserDiodeHours'] = None
    meta['laserDiodeTemp'] = None
    meta['viscosity'] = None

    meta['aodDetectorOffsetX'] = None
    meta['aodDetectorOffsetY'] = None
    meta['pmDetectorOffsetX'] = None
    meta['pmDetectorOffsetY'] = None

    meta['pmDistanceConversionX'] = None
    meta['pmDistanceConversionY'] = None
    meta['aodDistanceConversionX'] = None
    meta['aodDistanceConversionY'] = None

    meta['pmDisplacementSensitivityX'] = None
    meta['pmDisplacementSensitivityY'] = None
    meta['aodDisplacementSensitivityX'] = None
    meta['aodDisplacementSensitivityY'] = None

    meta['pmStiffnessX'] = None
    meta['pmStiffnessY'] = None
    meta['aodStiffnessX'] = None
    meta['aodStiffnessY'] = None

    meta['pmBeadDiameter'] = None
    meta['aodBeadDiameter'] = None
    meta['pmBeadRadius'] = None
    meta['pmBeadRadius'] = None

    meta['timeStep'] = None
    meta['samplingRate'] = None
    meta['recordingRate'] = None

    meta['andorAodCenterX'] = None
    meta['andorAodCenterY'] = None
    meta['andorAodRangeX'] = None
    meta['andorAodRangeY'] = None

    meta['ccdAodCenterX'] = None
    meta['ccdAodCenterY'] = None
    meta['ccdAodRangeX'] = None
    meta['ccdAodRangeY'] = None

    meta['andorPmCenterX'] = None
    meta['andorPmCenterY'] = None
    meta['andorPmRangeX'] = None
    meta['andorPmRangeY'] = None

    meta['ccdPmCenterX'] = None
    meta['ccdPmCenterY'] = None
    meta['ccdPmRangeX'] = None
    meta['ccdPmRangeY'] = None

    meta['andorPixelSizeX'] = None
    meta['andorPixelSizeY'] = None

    meta['ccdPixelSizeX'] = None
    meta['ccdPixelSizeY'] = None

    meta['samplingRate'] = None
    meta['nSamples'] = None
    meta['deltaTime'] = None

    for line in comment_list:
        if 'Date' in line:
            date_string = line.split(": ")[-1].replace("\t", " ")
        elif 'starttime' in line:
            time_string = line.strip().split(": ")[-1]
        elif 'Time of Experiment' in line:
            time_string = None
        elif 'Laser Diode Status' in line:
            pass
        elif 'thermal calibration' in line:
            pass
        elif 'data averaged to while-loop' in line:
            if 'FALSE' in line:
                isDataAveraged = False
            else:
                isDataAveraged = True

            meta['isDataAveraged'] = isDataAveraged

        elif 'errors' in line:
            error_string = line.split(": ")[-1]
            errors = [int(e) for e in error_string.split("\t")]
            if any(errors):
                hasErrors = True
            else:
                hasErrors = False

            meta['errors'] = errors
            meta['hasErrors'] = hasErrors

        elif 'number of samples' in line:
            try:
                nSamples = int(float(line.strip().split(": ")[-1]))
            except:
                nSamples = 1

            meta['nSamples'] = nSamples

        elif 'sample rate' in line:
            try:
                samplingRate = int(float(line.strip().split(": ")[-1]))
            except:
                samplingRate = 10000

            meta['samplingRate'] = samplingRate

        elif 'rate of while-loop' in line:
            try:
                recordingRate = int(float(line.strip().split(": ")[-1]))
            except:
                recordingRate = 10000

            meta['recordingRate'] = recordingRate

        elif 'duration of measurement' in line:
            try:
                duration = int(float(line.strip().split(": ")[-1]))
            except:
                duration = 0

            units['duration'] = 's'
            meta['duration'] = duration

        elif 'AOD detector horizontal offset' in line:
            try:
                aodDetectorOffsetX = float(line.strip().split(": ")[-1])
            except:
                aodDetectorOffsetX = 0

            units['aodDetectorOffsetX'] = 'V'
            meta['aodDetectorOffsetX'] = aodDetectorOffsetX

        elif 'AOD detector vertical offset' in line:
            try:
                aodDetectorOffsetY = float(line.strip().split(": ")[-1])
            except:
                aodDetectorOffsetY = 0

            units['aodDetectorOffsetY'] = 'V'
            meta['aodDetectorOffsetY'] = aodDetectorOffsetY

        elif 'PM detector horizontal offset' in line:
            try:
                pmDetectorOffsetX = float(line.strip().split(": ")[-1])
            except:
                pmDetectorOffsetX = 0

            units['pmDetectorOffsetX'] = 'V'
            meta['pmDetectorOffsetX'] = pmDetectorOffsetX

        elif 'PM detector vertical offset' in line:
            try:
                pmDetectorOffsetY = float(line.strip().split(": ")[-1])
            except:
                pmDetectorOffsetY = 0

            units['pmDetectorOffsetY'] = 'V'
            meta['pmDetectorOffsetY'] = pmDetectorOffsetY

        elif 'PM horizontal trap stiffness' in line:
            try:
                pmStiffnessX = float(line.strip().split(": ")[-1])
            except:
                pmStiffnessX = None

            meta['pmStiffnessX'] = pmStiffnessX

        elif 'PM vertical trap stiffness' in line:
            try:
                pmStiffnessY = float(line.strip().split(": ")[-1])
            except:
                pmStiffnessY = None

            meta['pmStiffnessY'] = pmStiffnessY
            
        elif 'AOD horizontal trap stiffness' in line:
            try:
                aodStiffnessX = float(line.strip().split(": ")[-1])
            except:
                aodStiffnessX = None

            meta['aodStiffnessX'] = aodStiffnessX
            
        elif 'AOD vertical trap stiffness' in line:
            try:
                aodStiffnessY = float(line.strip().split(": ")[-1])
            except:
                aodStiffnessY = None

            meta['aodStiffnessY'] = aodStiffnessY
            
        elif 'PM horizontal OLS' in line:
            try:
                pmDisplacementSensitivityX = float(line.strip().split(": ")[-1])
            except:
                pmDisplacementSensitivityX = None

            meta['pmDisplacementSensitivityX'] = pmDisplacementSensitivityX
            meta['pmDistanceConversionX'] = pmDisplacementSensitivityX
            
        elif 'PM vertical OLS' in line:
            try:
                pmDisplacementSensitivityY = float(line.strip().split(": ")[-1])
            except:
                pmDisplacementSensitivityY = None

            meta['pmDisplacementSensitivityY'] = pmDisplacementSensitivityY
            meta['pmDistanceConversionY'] = pmDisplacementSensitivityY
            
        elif 'AOD horizontal OLS' in line:
            try:
                aodDisplacementSensitivityX = float(line.strip().split(": ")[-1])
            except:
                aodDisplacementSensitivityX = None

            meta['aodDisplacementSensitivityX'] = aodDisplacementSensitivityX
            meta['aodDistanceConversionX'] = aodDisplacementSensitivityX
            
        elif 'AOD vertical OLS' in line:
            try:
                aodDisplacementSensitivityY = float(line.strip().split(": ")[-1])
            except:
                aodDisplacementSensitivityY = None

            meta['aodDisplacementSensitivityY'] = aodDisplacementSensitivityY
            meta['aodDistanceConversionY'] = aodDisplacementSensitivityY
            
        elif 'Viscosity' in line:
            try:
                viscosity = float(line.strip().split(": ")[-1])
            except:
                viscosity = 0.8902e-9 # viscosity of water @ 25C

            units['viscosity'] = 'pN s / nm^2'
            meta['viscosity'] = viscosity

        elif 'dt ' in line:
            try:
                dt = float(line.strip().split(": ")[-1])
            except:
                dt = 0.0010

            units['dt'] = units['timeStep'] = 's'
            meta['dt'] = meta['timeStep'] = dt 

        elif 'PM bead diameter' in line:
            try:
                pmBeadDiameter = float(line.strip().split(": ")[-1])
                if pmBeadDiameter < 20:
                    pmBeadDiameter = pmBeadDiameter * 1000
                elif '(um)' in line:
                    pmBeadDiameter = pmBeadDiameter * 1000
            except:
                pmBeadDiameter = 0

            pmBeadRadius = pmBeadDiameter / 2.0

            meta['pmBeadDiameter'] = pmBeadDiameter
            meta['pmBeadRadius'] = pmBeadRadius

        elif 'AOD bead diameter' in line:
            try:
                aodBeadDiameter = float(line.strip().split(": ")[-1])
                if aodBeadDiameter < 20:
                    aodBeadDiameter = aodBeadDiameter * 1000
                elif '(um)' in line:
                    aodBeadDiameter = aodBeadDiameter * 1000
            except:
                aodBeadDiameter = 0

            aodBeadRadius = aodBeadDiameter / 2.0

            meta['aodBeadDiameter'] = aodBeadDiameter
            meta['aodBeadRadius'] = aodBeadRadius

        elif 'Laser Diode Temp' in line:
            laserDiodeTemp = float(line.strip().split(": ")[-1])
            meta['laserDiodeTemp'] = laserDiodeTemp

        elif 'Laser Diode Operating Hours' in line:
            laserDiodeHours = float(line.strip().split(": ")[-1])
            meta['laserDiodeHours'] = laserDiodeHours

        elif 'Laser Diode Current' in line:
            laserDiodeCurrent = float(line.strip().split(": ")[-1])
            meta['laserDiodeCurrent'] = laserDiodeCurrent

        elif 'AOD ANDOR center x' in line:
            andorAodCenterX = float(line.strip().split(": ")[-1])
            meta['andorAodCenterX'] = andorAodCenterX

        elif 'AOD ANDOR center y' in line:
            andorAodCenterY = float(line.strip().split(": ")[-1])
            meta['andorAodCenterY'] = andorAodCenterY

        elif 'AOD ANDOR range x' in line:
            andorAodRangeX = float(line.strip().split(": ")[-1])
            meta['andorAodRangeX'] = andorAodRangeX

        elif 'AOD ANDOR range y' in line:
            andorAodRangeY = float(line.strip().split(": ")[-1])
            meta['andorAodRangeY'] = andorAodRangeY

        elif 'AOD CCD center x' in line:
            ccdAodCenterX = float(line.strip().split(": ")[-1])
            meta['ccdAodCenterX'] = ccdAodCenterX

        elif 'AOD CCD center y' in line:
            ccdAodCenterY = float(line.strip().split(": ")[-1])
            meta['ccdAodCenterY'] = ccdAodCenterY

        elif 'AOD CCD range x' in line:
            ccdAodRangeX = float(line.strip().split(": ")[-1])
            meta['ccdAodRangeX'] = ccdAodRangeX

        elif 'AOD CCD range y' in line:
            ccdAodRangeY = float(line.strip().split(": ")[-1])
            meta['ccdAodRangeY'] = ccdAodRangeY

        elif 'PM ANDOR center x' in line:
            andorPmCenterX = float(line.strip().split(": ")[-1])
            meta['andorPmCenterX'] = andorPmCenterX

        elif 'PM ANDOR center y' in line:
            andorPmCenterY = float(line.strip().split(": ")[-1])
            meta['andorPmCenterY'] = andorPmCenterY

        elif 'PM ANDOR range x' in line:
            andorPmRangeX = float(line.strip().split(": ")[-1])
            meta['andorPmRangeX'] = andorPmRangeX

        elif 'PM ANDOR range y' in line:
            andorPmRangeY = float(line.strip().split(": ")[-1])
            meta['andorPmRangeY'] = andorPmRangeY

        elif 'PM CCD center x' in line:
            ccdPmCenterX = float(line.strip().split(": ")[-1])
            meta['ccdPmCenterX'] = ccdPmCenterX

        elif 'PM CCD center y' in line:
            ccdPmCenterY = float(line.strip().split(": ")[-1])
            meta['ccdPmCenterY'] = ccdPmCenterY

        elif 'PM CCD range x' in line:
            ccdPmRangeX = float(line.strip().split(": ")[-1])
            meta['ccdPmRangeX'] = ccdPmRangeX

        elif 'PM CCD range y' in line:
            ccdPmRangeY = float(line.strip().split(": ")[-1])
            meta['ccdPmRangeY'] = ccdPmRangeY

        elif 'ANDOR pixel size x' in line:
            andorPixelSizeX = float(line.strip().split(": ")[-1])
            meta['andorPixelSizeX'] = andorPixelSizeX

        elif 'ANDOR pixel size y' in line:
            andorPixelSizeY = float(line.strip().split(": ")[-1])
            meta['andorPixelSizeY'] = andorPixelSizeY

        elif 'CCD pixel size x' in line:
            ccdPixelSizeX = float(line.strip().split(": ")[-1])
            meta['ccdPixelSizeX'] = ccdPixelSizeX

        elif 'CCD pixel size y' in line:
            ccdPixelSizeY = float(line.strip().split(": ")[-1])
            meta['ccdPixelSizeY'] = ccdPixelSizeY

        elif 'AOD detector x offset' in line:
            aodDetectorOffsetX = float(line.strip().split(": ")[-1])
            meta['aodDetectorOffsetX'] = aodDetectorOffsetX

        elif 'AOD detector y offset' in line:
            aodDetectorOffsetY = float(line.strip().split(": ")[-1])
            meta['aodDetectorOffsetY'] = aodDetectorOffsetY

        elif 'AOD trap stiffness x' in line:
            aodStiffnessX = float(line.strip().split(": ")[-1])
            meta['aodStiffnessX'] = aodStiffnessX

        elif 'AOD trap stiffness y' in line:
            aodStiffnessY = float(line.strip().split(": ")[-1])
            meta['aodStiffnessY'] = aodStiffnessY

        elif 'AOD trap distance conversion x' in line:
            aodDistanceConversionX = float(line.strip().split(": ")[-1])
            meta['aodDistanceConversionX'] = aodDistanceConversionX

        elif 'AOD trap distance conversion y' in line:
            aodDistanceConversionY = float(line.strip().split(": ")[-1])
            meta['aodDistanceConversionY'] = aodDistanceConversionY

        elif 'PM detector x offset' in line:
            pmDetectorOffsetX = float(line.strip().split(": ")[-1])
            meta['pmDetectorOffsetX'] = pmDetectorOffsetX

        elif 'PM detector y offset' in line:
            pmDetectorOffsetY = float(line.strip().split(": ")[-1])
            meta['pmDetectorOffsetY'] = pmDetectorOffsetY

        elif 'PM trap stiffness x' in line:
            pmStiffnessX = float(line.strip().split(": ")[-1])
            meta['pmStiffnessX'] = pmStiffnessX

        elif 'PM trap stiffness y' in line:
            pmStiffnessY = float(line.strip().split(": ")[-1])
            meta['pmStiffnessY'] = pmStiffnessY

        elif 'PM trap distance conversion x' in line:
            pmDistanceConversionX = float(line.strip().split(": ")[-1])
            meta['pmDistanceConversionX'] = pmDistanceConversionX

        elif 'PM trap distance conversion y' in line:
            pmDistanceConversionY = float(line.strip().split(": ")[-1])
            meta['pmDistanceConversionY'] = pmDistanceConversionY

        elif 'AOD bead radius' in line:
            try:
                aodBeadRadius = float(line.strip().split(": ")[-1])
                if aodBeadRadius < 20:
                    aodBeadRadius = aodBeadRadius * 1000
                elif '(um)' in line:
                    aodBeadRadius = aodBeadRadius * 1000
            except:
                aodBeadRadius = 0

            aodBeadDiameter = 2.0 * aodBeadRadius

            meta['aodBeadDiameter'] = round(aodBeadDiameter, 2)
            meta['aodBeadRadius'] = round(aodBeadRadius, 2)

        elif 'PM bead radius ' in line:
            try:
                pmBeadRadius = float(line.strip().split(": ")[-1])
                if pmBeadRadius < 20:
                    pmBeadRadius = pmBeadRadius * 1000
                elif '(um)' in line:
                    pmBeadRadius = pmBeadRadius * 1000
            except:
                pmBeadRadius = 0

            pmBeadDiameter = 2.0 * pmBeadRadius

            meta['pmBeadDiameter'] = round(pmBeadDiameter, 2)
            meta['pmBeadRadius'] = round(pmBeadRadius, 2)

        elif 'Sample rate' in line:
            samplingRate = float(line.strip().split(": ")[-1])
            meta['samplingRate'] = samplingRate

        elif 'Number of samples' in line:
            nSamples = float(line.strip().split(": ")[-1])
            meta['nSamples'] = nSamples

        elif 'Delta time' in line:
            deltaTime = float(line.strip().split(": ")[-1])
            meta['deltaTime'] = deltaTime

        elif 'Laser Diode Operating Hours' in line:
            try:
                laserDiodeHours = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeHours = 0

            meta['laserDiodeHours'] = laserDiodeHours
            units['laserDiodeHours'] = 'h'

        elif 'Laser Diode Current' in line:
            try:
                laserDiodeCurrent = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeCurrent = 0

            meta['laserDiodeCurrent'] = laserDiodeCurrent
            units['laserDiodeCurrent'] = 'A'

        elif 'Laser Diode Temp' in line:
            try:
                laserDiodeTemp = round(float(line.strip().split(": ")[-1]))
            except:
                laserDiodeTemp = 0

            meta['laserDiodeTemp'] = laserDiodeTemp
            units['laserDiodeTemp'] = 'C'

        else:
            if ":" in line:
                parts = line.split(": ")
            elif re.search('\w\s(\d|-\d)', line):
                parts = line.split(" ")

            if "." in parts[0]:
                var, unit, value = parts[0].split(".")[0], parts[0].split(".")[1], float(parts[1])
            else:
                var, unit, value = parts[0], None, float(parts[1])

            units[var] = unit
            meta[var] = value

    # parsing the date
    if date_string and time_string:
        combined_date = " ".join([date_string.strip(), time_string.strip()])
        date = datetime.datetime.strptime(combined_date, '%m/%d/%Y %I:%M %p')
    else:
        date = datetime.datetime.now()

    meta['date'] = date

    CommentInfo = namedtuple('CommentInfo', ['metadata', 'units'])
    C = CommentInfo(meta, units)

    return C


def simplify_tweebot_data_names(variable_names):
    """
    Extracts tweebot variable names from a list of variables and substitutes them for common tweezer nomenclature
    
    :param variable_names: (list) with variable names as read by tweebot datalog reader

    :return names: (list) new list with simpler variable names

    :return units: (dict) with the corresponding units of the variable names
    """
    units = {}
    names = copy.copy(variable_names)
    if 'Time sent (s)' in names:
        names[names.index('Time sent (s)')] = 'timeSent'
        units['timeSent'] = 's'

    if 'Time received (s)' in names:
        names[names.index('Time received (s)')] = 'timeReceived'
        units['timeReceived'] = 's'

    if 'Experiment Phase (int)' in names:
        names[names.index('Experiment Phase (int)')] = 'experimentPhase'
        units['experimentPhase'] = 'int'

    if 'Message index (int)' in names:
        names[names.index('Message index (int)')] = 'mIndex'
        units['mIndex'] = None

    if 'Extension from Trap and PSD positions (nm)' in names:
        names[names.index('Extension from Trap and PSD positions (nm)')] = 'extensionByTrap'
        units['extensionByTrap'] = 'nm'

    if 'Extension from image measurements (nm)' in names:
        names[names.index('Extension from image measurements (nm)')] = 'extenstionByImage'
        units['extenstionByImage'] = 'nm'

    if 'Force felt by AOD (pN)' in names:
        names[names.index('Force felt by AOD (pN)')] = 'forceAod'
        units['forceAod'] = 'pN'

    if 'Force felt by PM  (pN)' in names:
        names[names.index('Force felt by PM  (pN)')] = 'forcePm'
        units['forcePm'] = 'pN'

    if 'AOD to PM vector x (nm)' in names:
        names[names.index('AOD to PM vector x (nm)')] = 'trapSeparationX'
        units['trapSeparationX'] = 'nm'

    if 'AOD to PM vector y (nm)' in names:
        names[names.index('AOD to PM vector y (nm)')] = 'trapSeparationY'
        units['trapSeparationY'] = 'nm'

    if 'AODx (V)' in names:
        names[names.index('AODx (V)')] = 'dispAodX'
        units['dispAodX'] = 'V'

    if 'AODy (V)' in names:
        names[names.index('AODy (V)')] = 'dispAodY'
        units['dispAodX'] = 'V'

    if 'PMx (V)' in names:
        names[names.index('PMx (V)')] = 'dispPmX'
        units['dispPmX'] = 'V'

    if 'PMy (V)' in names:
        names[names.index('PMy (V)')] = 'dispPmY'
        units['dispPmY'] = 'V'

    if 'PMsensorx (V)' in names:
        names[names.index('PMsensorx (V)')] = 'mirrorX'
        units['mirrorX'] = 'V'

    if 'PMsensory (V)' in names:
        names[names.index('PMsensory (V)')] = 'mirrorY'
        units['mirrorY'] = 'V'

    if 'PMxdiff (V)' in names:
        names[names.index('PMxdiff (V)')] = 'pmX'
        units['pmX'] = 'V'

    if 'PMydiff (V)' in names:
        names[names.index('PMydiff (V)')] = 'pmY'
        units['pmY'] = 'V'

    if 'PMxsum (V)' in names:
        names[names.index('PMxsum (V)')] = 'pmSum'
        units['pmSum'] = 'V'

    if 'AODxdiff (V)' in names:
        names[names.index('AODxdiff (V)')] = 'aodX'
        units['aodX'] = 'V'

    if 'AODydiff (V)' in names:
        names[names.index('AODydiff (V)')] = 'aodY'
        units['aodY'] = 'V'

    if 'AODxsum (V)' in names:
        names[names.index('AODxsum (V)')] = 'aodSum'
        units['aodSum'] = 'V'

    if 'StageX (mm)' in names:
        names[names.index('StageX (mm)')] = 'stageX'
        units['stageX'] = 'nm'

    if 'StageY (mm)' in names:
        names[names.index('StageY (mm)')] = 'stageY'
        units['stageY'] = 'nm'

    if 'StageZ (mm)' in names:
        names[names.index('StageZ (mm)')] = 'stageZ'
        units['stageZ'] = 'nm'

    if 'Pressure (a.u.)' in names:
        names[names.index('Pressure (a.u.)')] = 'pressure'
        units['pressure'] = 'a.u.'

    if 'FBx (V)' in names:
        names[names.index('FBx (V)')] = 'fbX'
        units['fbX'] = 'V'

    if 'FBy (V)' in names:
        names[names.index('FBy (V)')] = 'fbY'
        units['fbY'] = 'V'

    if 'FBsum(V)' in names:
        names[names.index('FBsum (V)')] = 'fbZ'
        units['fbZ'] = 'V'

    return names, units

