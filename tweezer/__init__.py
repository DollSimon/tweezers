from __future__ import print_function, division

__doc__ = """\
Package for data analysis of optical trap experiments
"""

import os
import re
import glob

from functools import partial

from tweezer.core.parsers import classify

ALLFILES = glob.glob(os.path.dirname(__file__) + "/*.py")

__all__ = [os.path.basename(f)[:-3] for f in ALLFILES]

__version__ = (0, 0, 1)

_ROOT = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_SETTINGS = os.path.join(_ROOT, 'data', 'settings',
                                 'default_settings.json')

_INSTRUMENT_SETTINGS = os.path.join(_ROOT, 'data', 'settings',
                                    'instrument_settings.json')

_TWEEBOT_CONFIG_TXT = os.path.join(_ROOT, 'data', 'settings',
                                   'default.config.txt')

_TWEEBOT_CONFIG = os.path.join(_ROOT, 'data', 'settings',
                               'tweebot_configuration.json')


def get_example_path(path, example_type='data'):
    return os.path.join(_ROOT, example_type, path)


def path_to_sample_data(data_type='MAN_DATA', info=False):
    """
    Points to tweezer example data of a given data type.

    :param data_type: (Str) that represents the type of the data, like \
    'MAN_DATA', 'BOT_LOGS' or 'TC'
    :param info: (Boolean) if true just prints the available files

    :return example_file: archetype of the specified file type
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

    file_mapper = {'man_data': to_file(get_example_path('man_data'), location=-2),
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
        return file_mapper.get(data_type.lower(), 'unknown')
    else:
        print('The following file types are available:\n')
        for k in file_mapper:
            print(k)


def path_to_sample_dir(data_type='MAN_DATA'):
    """
    Points to tweezer example data of a given data type.

    :param data_type: (Str) that represents the type of the data, like \
    'MAN_DATA', 'BOT_LOGS' or 'TC'
    """
    data_type = data_type.upper()

    if data_type == 'MAN_DATA':
        path = get_example_path('man_data')
    elif data_type == 'BOT_DATA':
        path = get_example_path('bot_data')
    elif data_type == 'BOT_STATS':
        path = get_example_path('bot_stats')
    elif data_type == 'BOT_LOG':
        path = get_example_path('bot_logs')
    elif data_type == 'BOT_FOCUS':
        path = get_example_path('bot_focus')
    elif data_type == 'BOT_ANDOR':
        path = get_example_path('bot_andor')
    elif data_type == 'BOT_TDMS':
        path = get_example_path('bot_tdms')
    elif data_type == 'MAN_DIST_CAL_':
        path = get_example_path('man_dist_cal')
    elif data_type == 'TC':
        path = get_example_path('thermal_calibration')
    elif data_type == 'MAN_TRACK':
        path = get_example_path('man_track')
    elif data_type == 'MAN_FLOW':
        path = get_example_path('man_flow')

    return path


def path_to_templates(data_type='PYTEX'):
    """
    Points to tweezer templates for automatic report generation.

    :param data_type: (Str) that represents the type of the data, like \
    'MAN_DATA', 'BOT_LOGS' or 'TC'
    """
    data_type = data_type.upper()

    if data_type == 'PYTEX':
        path = get_example_path('pytex', example_type='templates')
    elif data_type == 'KNITR':
        path = get_example_path('knitr')

    return path


def read(file_name, file_type='man_data', **kwargs):
    """
    Convenience function to read the data from a given tweezer file name into \
    a pandas DataFrame. It tries to make an educated guess about the file_type\
    of the file in question and to dispatch the appropriate function call.

    :param file_name: (path) to the file to be read into a pandas.DataFrame

    :return data: (pandas.DataFrame) If applicable this return type contains \
    the time series data in a DataFrame and any metadata as its attributes
    """
    from tweezer.io import (read_tdms,
                            read_tweebot_data,
                            read_tweebot_logs,
                            read_tweezer_image_info,
                            read_tracking_data,
                            read_tweezer_txt,
                            read_thermal_calibration,
                            read_tweezer_power_spectrum)

    # classify file
    try:
        ftype = classify(file_name)
        if 'unknown' in ftype.lower():
            ftype = file_type
    except:
        print("Can't classify the file type myself. Trying the file_type \
            default ('man_data')")
        ftype = file_type

    if 'frequency' in kwargs:
        f = kwargs['frequency']
        read_tweezer_power_spectrum = partial(read_tweezer_power_spectrum,
                                              frequency=f)

        read_tdms = partial(read_tdms, frequency=f)

    # use dictionary to dispatch the appropriate function
    # (functions are first-class citizens!)
    read_mapper = {
        'man_data': read_tweezer_txt,
        'man_pics': read_tweezer_image_info,
        'man_track': read_tracking_data,
        'tc_psd': read_tweezer_power_spectrum,
        'tc_ts': read_thermal_calibration,
        'bot_data': read_tweebot_data,
        'bot_tdms': read_tdms,
        'bot_log': read_tweebot_logs
    }

    data = read_mapper[ftype.lower()](file_name)

    return data


## Python 2 to 3 conversion related things
## see: http://lucumr.pocoo.org/2013/5/21/porting-to-python-3-redux/
import sys
PY2 = sys.version_info[0] == 2
if not PY2:
    text_type = str
    string_types = (str,)
    unichr = chr
else:
    text_type = unicode
    string_types = (str, unicode)
    unichr = unichr
