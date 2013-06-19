from __future__ import print_function, division

__doc__ = """\
Package for data analysis of optical trap experiments
"""

import os
import glob

__all__ = [ os.path.basename(f)[:-3] for f in glob.glob(os.path.dirname(__file__)+"/*.py")]

__version__ = (0, 0, 1)

_ROOT = os.path.abspath(os.path.dirname(__file__))

_DEFAULT_SETTINGS = os.path.join(_ROOT, 'data', 'settings', 'default_settings.json')

_TWEEBOT_CONFIG_TXT = os.path.join(_ROOT, 'data', 'settings', 'default.config.txt')

def get_example_path(path, example_type='data'):
    return os.path.join(_ROOT, example_type, path)


def path_to_sample_data(data_type = 'MAN_DATA'):
    """
    Points to tweezer example data of a given data type.

    :param data_type: (Str) that represents the type of the data, like 'MAN_DATA', 'BOT_LOGS' or 'TC'
    :return example_file: archetype of the specified file type
    
    """
    data_type = data_type.upper()

    def to_file(path, location=-1):
        return os.path.join(path, os.listdir(path)[location])

    if data_type == 'MAN_DATA':
        example_file = to_file(get_example_path('man_data'), location=-2)
    elif data_type == 'BAD_MAN_DATA':
        example_file = to_file(get_example_path('man_data'))
    elif data_type == 'BOT_DATA':
        example_file = to_file(get_example_path('bot_data'))
    elif data_type == 'BOT_STATS':
        example_file = to_file(get_example_path('bot_stats'))
    elif data_type == 'BOT_LOG':
        example_file = to_file(get_example_path('bot_logs'))
    elif data_type == 'BOT_FOCUS':
        example_file = to_file(get_example_path('bot_focus'))
    elif data_type == 'BOT_ANDOR':
        example_file = to_file(get_example_path('bot_andor'))
    elif data_type == 'BOT_TDMS':
        example_file = to_file(get_example_path('bot_tdms'))
        if '.tdms_index' in os.path.splitext(example_file)[1]:
            example_file = "".join([os.path.splitext(example_file)[0], '.tdms'])
    elif data_type == 'MAN_DIST_CAL_':
        example_file = to_file(get_example_path('man_dist_cal'))
    elif data_type == 'TC_TS':
        example_file = to_file(get_example_path('thermal_calibration'))
    elif data_type == 'TC_PSD':
        example_file = to_file(get_example_path('thermal_calibration'), location=-2)
    elif data_type == 'MAN_TRACK':
        example_file = to_file(get_example_path('man_track'))
    elif data_type == 'MAN_FLOW':
        example_file = to_file(get_example_path('man_flow'))
    else:
        example_file = "unknown"

    return example_file


def path_to_sample_dir(data_type = 'MAN_DATA'):
    """
    Points to tweezer example data of a given data type.

    :param data_type: (Str) that represents the type of the data, like 'MAN_DATA', 'BOT_LOGS' or 'TC'
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


def path_to_templates(data_type = 'PYTEX'):
    """
    Points to tweezer templates for automatic report generation.

    :param data_type: (Str) that represents the type of the data, like 'MAN_DATA', 'BOT_LOGS' or 'TC'
    """
    data_type = data_type.upper()

    if data_type == 'PYTEX':
        path = get_example_path('pytex', example_type = 'templates')
    elif data_type == 'KNITR':
        path = get_example_path('knitr')

    return path


def read(file_name, file_type='man_data'):
    """
    Convenience function to read the data from a given tweezer file name into a pandas DataFrame. It tries to make an educated guess about the file_type of the file in question and to dispatch the appropriate function call.
    
    :param file_name: (path) to the file to be read into a pandas.DataFrame

    :return data: (pandas.DataFrame) If applicable this return type contains the time series data in a DataFrame and any metadata as its attributes
    """
    raise NotImplementedError("WIP: {}.read".format(__name__))
    
