import pytest

from tweezer.io import read_tweebot_data_header
from tweezer import path_to_sample_data

# get example file
bot_file = path_to_sample_data('bot_data')


def test_bot_header_can_be_read():
    header = read_tweebot_data_header(bot_file)
    assert header is not None


def test_header_values():
    header = read_tweebot_data_header(bot_file)
    assert header.units['timeStep'] == 's'


