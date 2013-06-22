#!/usr/bin/env python
#-*- coding: utf-8 -*-

import copy

import pandas as pd



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


def combine_tweebot_data(datalog_content=pd.DataFrame([]), tdms_content=pd.DataFrame([])):
    """
    Aligns the data from different sources, most notably from Tweebot Datalog files and from TDMS files.
    
    :param datalog_content: (pandas.DataFrame) of 
    :param tdms_content: (pandas.DataFrame) of high frequency tdms data
    """
    dc = datalog_content
    tc = tdms_content

    pass
    # get attributes

    # find common values in column....
    # where is dc.pressure == tc.pressure

    # combine attributes
    # 
