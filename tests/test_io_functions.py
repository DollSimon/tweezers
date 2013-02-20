import unittest
from tweezer.io import is_calibration_time_series as is_ts
from tweezer.io import is_calibration_spectrum as is_sp
from tweezer.io import is_tweebot_datalog as is_dl
from tweezer.io import is_tweebot_stats as is_st
from tweezer.io import is_tweebot_log as is_tl
from tweezer.io import is_tweezer_data as is_td

def test_is_calibration_time_series():
    valid_files = ['TS_1.txt', 'TS_1_3.txt', 'TS_12.txt', 'TS_23_a.txt', 'TS_run_1_3.txt']

    invalid_files = ['PSD_1.txt', 'Rocket.m', 'TS.txt', 'Data_1_3434_a.txt', 'TS_1_3.m']

    print(is_ts('TS_1.txt'))
    assert is_ts('TS_1.txt') == True

    for index, file_name in enumerate(valid_files):
        print(index)
        assert is_ts(file_name) == True

    for index, file_name in enumerate(invalid_files):
        print(index)
        assert is_ts(file_name) == False


def test_is_calibration_spectrum():
    valid_files = ['PSD_1.txt', 'PSD_1_3.txt', 'PSD_12.txt', 'PSD_23_a.txt', 'PSD_run_1_3.txt']

    invalid_files = ['PSD_1.r', 'Rocket.m', 'PSD.txt', 'Data_1_3434_a.txt', 'PSD_1_3.m']

    print(is_sp('PSD_1.txt'))
    assert is_sp('PSD_1.txt') == True

    for index, file_name in enumerate(valid_files):
        print(index)
        assert is_sp(file_name) == True

    for index, file_name in enumerate(invalid_files):
        print(index)
        assert is_sp(file_name) == False

def test_is_tweebot_datalog():
    valid_files = ['27.Datalog.2013.02.17.19.42.09.datalog.txt', '79.Datalog.2012.11.27.05.47.17.datalog.txt']

    invalid_files = ['PSD_1.r', 'PSD_1_3.txt', 'Rocket.m', 'PSD.txt', 'Data_1_3434_a.txt', 'PSD_1_3.m', '46.TweeBotStats.txt', '27.TweeBotLog.2013.02.20.01.16.33.txt']

    print(is_dl('27.Datalog.2013.02.17.19.42.09.datalog.txt'))
    assert is_dl('27.Datalog.2013.02.17.19.42.09.datalog.txt') == True

    for index, file_name in enumerate(valid_files):
        print(index)
        assert is_dl(file_name) == True

    for index, file_name in enumerate(invalid_files):
        print(index)
        assert is_dl(file_name) == False

def test_is_tweebot_stats():
    valid_files = ['27.TweeBotStats.txt', '46.TweeBotStats.txt', '46.tweebotstats.txt']

    invalid_files = ['PSD_1.r', 'PSD_1_3.txt', 'Rocket.m', 'PSD.txt', 'Data_1_3434_a.txt', 'PSD_1_3.m', '27.Datalog.2013.02.17.19.42.09.datalog.txt', '27.TweeBotLog.2013.02.20.01.16.33.txt']

    print(is_st('27.TweeBotStats.txt'))
    assert is_st('27.TweeBotStats.txt') == True

    for index, file_name in enumerate(valid_files):
        print(index)
        assert is_st(file_name) == True

    for index, file_name in enumerate(invalid_files):
        print(index)
        assert is_st(file_name) == False

def test_is_tweebot_log():
    valid_files = ['27.TweeBotLog.2013.02.20.01.16.33.txt', '27.tweebotlog.2013.02.20.01.16.33.txt']

    invalid_files = ['PSD_1.r', 'PSD_1_3.txt', 'Rocket.m', 'PSD.txt', 'Data_1_3434_a.txt', 'PSD_1_3.m', '46.tweebotstats.txt', '27.Datalog.2013.02.17.19.42.09.datalog.txt', '27.TweeBotStat.2013.02.20.01.16.33.txt']

    print(is_tl('27.TweeBotLog.2013.02.20.01.16.33.txt'))
    assert is_tl('27.TweeBotLog.2013.02.20.01.16.33.txt') == True

    for index, file_name in enumerate(valid_files):
        print(index)
        assert is_tl(file_name) == True

    for index, file_name in enumerate(invalid_files):
        print(index)
        assert is_tl(file_name) == False

def test_is_tweezer_data():
    valid_files = ['27.txt', 'Data_34_a.txt', '23_A.txt']

    invalid_files = ['PSD_1.r', 'PSD_1_3.txt', 'Rocket.m', 'PSD.txt', 'PSD_1_3.m', '46.tweebotstats.txt', '27.Datalog.2013.02.17.19.42.09.datalog.txt', '27.TweeBotStat.2013.02.20.01.16.33.txt']

    print(is_td('27.txt'))
    assert is_td('27.txt') == True

    for index, file_name in enumerate(valid_files):
        print('{}: {}'.format(index, file_name))
        assert is_td(file_name) == True

    print(is_td('27.m'))

    for index, file_name in enumerate(invalid_files):
        print('{}: {}'.format(index, file_name))
        assert is_td(file_name) == False


class TestFileIdentity(unittest.TestCase):
    def setUp(self):
        print('Rackoon!')
        self.file = '27.txt'
        self.x = 4

    def test_truth(self):
        assert type(self.file) is str

    def test_false(self):
        assert True

    def test_math(self):
        assert self.x == 4
