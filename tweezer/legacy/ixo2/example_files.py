# coding=utf-8
import os
import re

from collections import namedtuple

from tweezer import _ROOT

_DEFAULT_SETTINGS = os.path.join(_ROOT, 'data', 'settings',
                                 'default_settings.json')

_INSTRUMENT_SETTINGS = os.path.join(_ROOT, 'data', 'settings',
                                    'instrument_settings.json')

_TWEEBOT_CONFIG_TXT = os.path.join(_ROOT, 'data', 'settings',
                                   'default.config.txt')

_TWEEBOT_CONFIG = os.path.join(_ROOT, 'data', 'settings',
                               'tweebot_configuration.json')


def get_example_path(subCategory='man_data', exampleType='data'):
    """
    Returns path to the example files.

    This is set relative to the package installation, so the data files can be found on
    different machines.

    Args:
        subCategory (str): identifier of the actual example file, like 'man_data', 'bot_data', etc.
                           (Default: 'man_data')
        exampleType (str): main category of the example files, like 'data', or 'templates'.
                           (Default: 'data')

    Returns:
        examplePath (str): to an example data file
    """
    return os.path.join(_ROOT, exampleType, subCategory)


def path_to_sample_data(dataType='MAN_DATA', info=False, returnType='file'):
    """
    Points to tweezer example data of a given data type.

    Args:
        dataType (str): that represents the type of the data, like 'MAN_DATA',
                        'BOT_LOGS' or 'TC'. (Default: 'MAN_DATA')
        info (bool): if true just prints the available files. (Default: False)
        returnType (str): either 'file' or 'dict' to return either single file or
                          collection of files

    Returns:
        exampleFile (str): full path to the archetype of the specified file type
        fileMapper (dict): collection of known example files
    """
    def to_file(path, location=-1):
        return os.path.join(path, os.listdir(path)[location])

    def find_file(path, name):
        files = [f for f in os.listdir(path) if re.search('^.+\.\w+$', f)]
        target = [f for f in files if name in f]
        if target:
            return os.path.join(path, target[0])
        else:
            return None

    fileMapper = {'man_data': to_file(get_example_path('man_data'), location=-2),
                  'data': to_file(get_example_path('man_data'), location=-2),
                  'bad_man_data': to_file(get_example_path('man_data')),
                  'bot_data': to_file(get_example_path('bot_data')),
                  'bot_stats': to_file(get_example_path('bot_stats'), location=-2),
                  'bot_log': to_file(get_example_path('bot_logs')),
                  'log': to_file(get_example_path('bot_logs')),
                  'bot_focus': to_file(get_example_path('bot_focus')),
                  'bot_tdms': to_file(get_example_path('bot_tdms'), location=-2),
                  'tdms': to_file(get_example_path('bot_tdms'), location=-2),
                  'bot_tdms_index': to_file(get_example_path('bot_tdms'), location=-2),
                  'tc_ts': to_file(get_example_path('thermal_calibration')),
                  'ts': to_file(get_example_path('thermal_calibration')),
                  'TS': to_file(get_example_path('thermal_calibration')),
                  'tc_psd': to_file(get_example_path('thermal_calibration'), location=-2),
                  'psd': to_file(get_example_path('thermal_calibration'), location=-2),
                  'PSD': to_file(get_example_path('thermal_calibration'), location=-2),
                  'man_track': to_file(get_example_path('man_track')),
                  'track': to_file(get_example_path('man_track')),
                  'dist_cal_pm_mat': find_file(get_example_path('man_dist_cal'), name='PM_calibration_pm2p'),
                  'pm_dist_cal_mat': find_file(get_example_path('man_dist_cal'), name='PM_calibration_pm2p'),
                  'pm_dist_cal': find_file(get_example_path('man_dist_cal'), name='PM_calibration_pm2p'),
                  'dist_cal_pm_res': find_file(get_example_path('man_dist_cal'), name='PM_calibration_calib_pm2pix'),
                  'pm_dist_cal_res': find_file(get_example_path('man_dist_cal'), name='PM_calibration_calib_pm2pix'),
                  'dist_cal_aod_res': find_file(get_example_path('man_dist_cal'), name='AOD_calibration_calib_aod2pix'),
                  'aod_dist_cal_res': find_file(get_example_path('man_dist_cal'), name='AOD_calibration_calib_aod2pix'),
                  'dist_cal_aod_mat': find_file(get_example_path('man_dist_cal'), name='AOD_calibration_aod2p'),
                  'aod_dist_cal_mat': find_file(get_example_path('man_dist_cal'), name='AOD_calibration_aod2p'),
                  'aod_dist_cal': find_file(get_example_path('man_dist_cal'), name='AOD_calibration_aod2p'),
                  'dist_cal_temp': find_file(get_example_path('man_dist_cal'), name='calibration_template_db_tb'),
                  'template': find_file(get_example_path('man_dist_cal'), name='calibration_template_db_tb'),
                  'man_flow': to_file(get_example_path('man_flow'))}

    if not info:
        exampleFile = fileMapper.get(dataType.lower(), 'unknown')
        if returnType == 'file':
            return exampleFile
        elif returnType == 'dict':
            return fileMapper
        else:
            print("Don't know what to return...")
    else:
        print('The following file types are available:\n')
        for k in fileMapper:
            print(k)


def path_to_sample_dir(dataType='MAN_DATA'):
    """
    Points to tweezer example data directory of a given data type.

    Args:
        dataType (str): that represents the type of the data, like 'MAN_DATA', 'BOT_LOGS' or 'TC'

    Returns:
        exampleDir (str): to an example data directory
    """
    dataType = dataType.upper()

    if dataType == 'MAN_DATA':
        exampleDir = get_example_path('man_data')
    elif dataType == 'BOT_DATA':
        exampleDir = get_example_path('bot_data')
    elif dataType == 'BOT_STATS':
        exampleDir = get_example_path('bot_stats')
    elif dataType == 'BOT_LOG':
        exampleDir = get_example_path('bot_logs')
    elif dataType == 'BOT_FOCUS':
        exampleDir = get_example_path('bot_focus')
    elif dataType == 'BOT_ANDOR':
        exampleDir = get_example_path('bot_andor')
    elif dataType == 'BOT_TDMS':
        exampleDir = get_example_path('bot_tdms')
    elif dataType == 'MAN_DIST_CAL_':
        exampleDir = get_example_path('man_dist_cal')
    elif dataType == 'TC':
        exampleDir = get_example_path('thermal_calibration')
    elif dataType == 'MAN_TRACK':
        exampleDir = get_example_path('man_track')
    elif dataType == 'MAN_FLOW':
        exampleDir = get_example_path('man_flow')

    return exampleDir


def path_to_templates(dataType='PYTEX'):
    """
    Points to tweezer templates for automatic report generation.

    Args:
        dataType (str): that represents the type of the data, like 'MAN_DATA', 'BOT_LOGS' or 'TC'

    Returns:
        templateDir (str): to a templates directory
    """
    dataType = dataType.upper()

    if dataType == 'PYTEX':
        templateDir = get_example_path('pytex', exampleType='templates')
    elif dataType == 'KNITR':
        templateDir = get_example_path('knitr')

    return templateDir


dataDict = path_to_sample_data(returnType='dict')

# Using dictionary unpacking to assign single nested dict to namedtuple
DataFiles = namedtuple("DataFiles", dataDict.keys())(**dataDict)

