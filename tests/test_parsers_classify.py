#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest
from nose.tools import *
import sure

from collections import namedtuple
from itertools import izip

from tweezer.core.parsers import classify, classify_all, parse_tweezer_file_name

# Valid TweeBot files
BOT_DATA = ['path/39.Datalog.2013.02.20.04.14.20.datalog.txt','39.Datalog.2013.02.20.04.14.20.datalog.txt']
BOT_LOG = 'path/56.TweeBotLog.2013.02.20.08.55.15.txt'
BOT_STATS = 'path/11.TweeBotStats.txt'
BOT_FOCUS = 'path/focussingstage.fullfocus12.focustable.txt'
BOT_SCRIPT = 'path/1.SavedTweeBotScript.2013.02.19.17.04.25.whole.groovy'
BOT_CCD = ['path/5.Snapshot..2013.02.19.18.26.16.584.ccd.png', '/Users/jahnel/code/example_data/tweebot/snapshots.ccd/18.Snapshot..2013.02.19.23.09.45.683.ccd.png']
BOT_ANDOR = ['path/1.Snapshot..2013.02.16.16.12.14.405.andor.png',
    '/Users/jahnel/code/example_data/tweebot/snapshots.andor/20.Snapshot..2013.02.19.23.32.30.254.andor.png'] 
BOT_TDMS = ['path/38_2013_05_14_16_43_43.tdms', '/Users/jahnel/code/example_data/tweebot/data/18_2013_05_19_17_18_07.tdms']

BOT_FILES = namedtuple('BOT_FILES', ['data', 'log', 'stats', 'focus', 'script', 'ccd', 'andor', 'tdms'])
bot = BOT_FILES(BOT_DATA, BOT_LOG, BOT_STATS, BOT_FOCUS, BOT_SCRIPT, BOT_CCD, BOT_ANDOR, BOT_TDMS)

# Valid Manual Tweezer Files
MAN_DATA = ['data/2_c.txt', 'data/5.txt', 'data/23_c.txt']

MAN_PM_DIST_CAL_RES = 'path/PM_calibration_calib_pm2pix.txt'
MAN_PM_DIST_CAL_MAT = 'path/PM_calibration_pm2p.txt'
MAN_PM_DIST_CAL_VID = 'path/PM_calibration_video.avi'

MAN_AOD_DIST_CAL_RES = 'path/AOD_calibration_calib_aod2pix.txt'
MAN_AOD_DIST_CAL_MAT = 'path/AOD_calibration_aod2p.txt'
MAN_AOD_DIST_CAL_VID = 'path/AOD_calibration_video.avi'

MAN_DIST_CAL_TMP = 'path/calibration_template_db_tb.tif'

MAN_VID = ['videos/4.avi', 'videos/4_c.avi']
MAN_PICS = ['pictures/4.jpg', 'pictures/5_r.jpg']
MAN_FLOW = ['flowcell/2.csv', 'flowcell/3_t.csv']
MAN_TRACK = ['tracking/2.csv', 'tracking/3_t.csv']
MAN_TMP = ['templates/4.tif', 'templates/2_a.tif']

# Valid files for both tweezer modes (e.g. thermal calibration)
TC_PSD = ['path/PSD_4_d.txt', 'path/PSD_5.txt', 'path/PSD_10.txt']
TC_TS = ['path/TS_4_d.txt', 'path/TS_5.txt', 'path/TS_10.txt']
ANDOR_VID = ['path/test.fits', 'path with whitespace/file with white space.fits']

MAN_FILES = namedtuple('MAN_FILES', ['data', 'pm_dist_cal_res', 'pm_dist_cal_mat', 'pm_dist_cal_vid','dist_cal_temp', 'aod_dist_cal_res', 'aod_dist_cal_mat', 'aod_dist_cal_vid', 'vid', 'pics', 'flow', 'track', 'tmp'])

man = MAN_FILES(MAN_DATA, MAN_PM_DIST_CAL_RES, MAN_PM_DIST_CAL_MAT, MAN_PM_DIST_CAL_VID, MAN_DIST_CAL_TMP, MAN_AOD_DIST_CAL_RES, MAN_AOD_DIST_CAL_MAT, MAN_AOD_DIST_CAL_VID, MAN_VID, MAN_PICS, MAN_FLOW, MAN_TRACK, MAN_TMP)

files = [f for f in man if not isinstance(f, list)] + [f for f in bot if not isinstance(f, list)]
files = files + [f for sublist in man for f in sublist if isinstance(sublist, list)]
files = files + [f for sublist in bot for f in sublist if isinstance(sublist, list)]
files = files + [f for f in TC_PSD]
files = files + [f for f in TC_TS]
files = files + [f for f in ANDOR_VID]

class TestFileParsing:

    @classmethod
    def setup_class(cls):
        print ("setup_class() before any methods in this class")
        types = classify_all(files)
        cls.mapping = {f:t for f, t in izip(files, types)}

    def test_tweebot_files(self):
        # infer valid files correctly
        mapping = self.__class__.mapping

        mapping[bot.data[0]].should.equal('BOT_DATA') 
        mapping[bot.data[1]].should.equal('BOT_DATA') 
        mapping[bot.log].should.equal('BOT_LOG') 
        mapping[bot.stats].should.equal('BOT_STATS') 
        mapping[bot.focus].should.equal('BOT_FOCUS') 
        mapping[bot.script].should.equal('BOT_SCRIPT') 
        mapping[bot.ccd[0]].should.equal('BOT_CCD') 
        mapping[bot.ccd[1]].should.equal('BOT_CCD') 
        mapping[bot.andor[0]].should.equal('BOT_ANDOR') 
        mapping[bot.andor[1]].should.equal('BOT_ANDOR') 
        mapping[bot.tdms[0]].should.equal('BOT_TDMS') 
        mapping[bot.tdms[1]].should.equal('BOT_TDMS') 

        # don't get confused on files that are not valid
        mapping[bot.log].shouldnot.equal('BOT_DATA') 
        mapping[bot.stats].shouldnot.equal('BOT_DATA') 
        mapping[bot.focus].shouldnot.equal('BOT_DATA') 

    def test_manunal_files(self):
        # infer valid files correctly
        mapping = self.__class__.mapping

        mapping[man.data[0]].should.equal('MAN_DATA')
        mapping[man.data[1]].should.equal('MAN_DATA')
        mapping[man.data[2]].should.equal('MAN_DATA')

        mapping[man.pm_dist_cal_res].should.equal('MAN_PM_DIST_CAL_RES')
        mapping[man.pm_dist_cal_mat].should.equal('MAN_PM_DIST_CAL_MAT')
        mapping[man.pm_dist_cal_vid].should.equal('MAN_PM_DIST_CAL_VID')

        mapping[man.aod_dist_cal_res].should.equal('MAN_AOD_DIST_CAL_RES')
        mapping[man.aod_dist_cal_mat].should.equal('MAN_AOD_DIST_CAL_MAT')
        mapping[man.aod_dist_cal_vid].should.equal('MAN_AOD_DIST_CAL_VID')

        mapping[man.dist_cal_temp].should.equal('MAN_DIST_CAL_TMP')
        mapping[man.vid[0]].should.equal('MAN_VID')
        mapping[man.vid[1]].should.equal('MAN_VID')
        mapping[man.flow[0]].should.equal('MAN_FLOW')
        mapping[man.flow[1]].should.equal('MAN_FLOW')
        mapping[man.pics[0]].should.equal('MAN_PICS')
        mapping[man.pics[1]].should.equal('MAN_PICS')
        mapping[man.track[0]].should.equal('MAN_TRACK')
        mapping[man.track[1]].should.equal('MAN_TRACK')
        mapping[man.tmp[0]].should.equal('MAN_TMP')
        mapping[man.tmp[1]].should.equal('MAN_TMP')


    def test_general_files(self):
        # infer valid files correctly
        mapping = self.__class__.mapping

        mapping[TC_PSD[0]].should.equal('TC_PSD')
        mapping[TC_PSD[1]].should.equal('TC_PSD')
        mapping[TC_PSD[2]].should.equal('TC_PSD')
        mapping[TC_TS[0]].should.equal('TC_TS')
        mapping[TC_TS[1]].should.equal('TC_TS')
        mapping[TC_TS[2]].should.equal('TC_TS')
        mapping[ANDOR_VID[0]].should.equal('ANDOR_VID')
        mapping[ANDOR_VID[1]].should.equal('ANDOR_VID')

    def test_bot_file_info_extraction(self):
        FI = parse_tweezer_file_name(bot.data[0])
        int(FI.trial).should.equal(39) 

    def test_manual_file_info_extraction(self):
        FI = parse_tweezer_file_name(man.data[0], parser='man_data')
        int(FI.trial).should.equal(2) 
        FI.subtrial.should.equal('c') 

        FI = parse_tweezer_file_name(man.flow[1], parser='man_data')
        int(FI.trial).should.equal(3) 
        FI.subtrial.should.equal('t') 
        
        


        
        

