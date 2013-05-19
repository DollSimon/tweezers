__all__ = ['io', 'utils', 'ixo', 'ott', 'gui', 'core', 'scripts', 'cli']

__version__ = (0, 0, 1)

import os

_ROOT = os.path.abspath(os.path.dirname(__file__))

def get_example_path(path, example_type='data'):
    return os.path.join(_ROOT, example_type, path)


def path_to_sample_data(data_type = 'MAN_DATA'):
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

