#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sure
import os

import tweezer
from tweezer import path_to_sample_data

_INSTALLATION_DIR = os.path.join(tweezer.__path__[0], 'data')

def test_path_to_sample_data():
    bot_data = path_to_sample_data('bot_data')
    man_data = path_to_sample_data('man_data')
    bad_man_data = path_to_sample_data('bad_man_data')
    bot_stats = path_to_sample_data('bot_stats')
    bot_log = path_to_sample_data('bot_log')
    bot_focus = path_to_sample_data('bot_focus')
    bot_tdms = path_to_sample_data('bot_tdms')
    tc_ts = path_to_sample_data('tc_ts')
    tc_psd = path_to_sample_data('tc_psd')

    dist_cal_pm_mat = path_to_sample_data('dist_cal_pm_mat')
    dist_cal_aod_mat = path_to_sample_data('dist_cal_aod_mat')

    dist_cal_pm_res = path_to_sample_data('dist_cal_pm_res')
    dist_cal_aod_res = path_to_sample_data('dist_cal_aod_res')

    dist_cal_temp = path_to_sample_data('dist_cal_temp')

    bot_data.should.equal(os.path.join(_INSTALLATION_DIR, 'bot_data/60.Datalog.2013.02.20.10.03.29.datalog.txt'))
    man_data.should.equal(os.path.join(_INSTALLATION_DIR, 'man_data/14_e.txt'))
    bad_man_data.should.equal(os.path.join(_INSTALLATION_DIR, 'man_data/5.txt'))
    bot_stats.should.equal(os.path.join(_INSTALLATION_DIR, 'bot_stats/32.TweeBotStats.txt'))
    bot_log.should.equal(os.path.join(_INSTALLATION_DIR, 'bot_logs/34.TweeBotLog.2013.05.19.02.14.53.txt'))
    bot_focus.should.equal(os.path.join(_INSTALLATION_DIR, 'bot_focus/focussingstage.refocus6.focustable.txt'))
    bot_tdms.should.equal(os.path.join(_INSTALLATION_DIR, 'bot_tdms/34_2013_05_19_02_34_37.tdms'))
    tc_psd.should.equal(os.path.join(_INSTALLATION_DIR, 'thermal_calibration/PSD_34.txt'))
    tc_ts.should.equal(os.path.join(_INSTALLATION_DIR, 'thermal_calibration/TS_34.txt'))

    dist_cal_aod_mat.should.equal(os.path.join(_INSTALLATION_DIR, 'man_dist_cal/AOD_calibration_aod2p.txt'))
    dist_cal_pm_mat.should.equal(os.path.join(_INSTALLATION_DIR, 'man_dist_cal/PM_calibration_pm2p.txt'))
    dist_cal_pm_res.should.equal(os.path.join(_INSTALLATION_DIR, 'man_dist_cal/PM_calibration_calib_pm2pix.txt'))
    dist_cal_aod_res.should.equal(os.path.join(_INSTALLATION_DIR, 'man_dist_cal/AOD_calibration_calib_aod2pix.txt'))
    dist_cal_temp.should.equal(os.path.join(_INSTALLATION_DIR, 'man_dist_cal/calibration_template_db_tb.tif'))
    

