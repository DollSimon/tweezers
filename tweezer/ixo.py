#!/usr/bin/env python
#-*- coding: utf-8 -*-

"""
General utility functions used for tweezer package.

"""
import os
import cProfile
import envoy
from collections import namedtuple


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
        'sampleRate',
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
        sampleRate=None,
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
        sampleRate,
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
            aodBeadRadius='um',
            pmBeadRadius='um',
            sampleRate='Hz',
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
            sampleRate,
            nSamples,
            deltaTime,
            timeStep)
