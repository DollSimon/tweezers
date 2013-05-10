import unittest
from nose.tools import *
import sure

from collections import namedtuple

from tweezer.core.polymer import ExtensibleWormLikeChain
from tweezer.core.parsers import classify


# Valid TweeBot files
BOT_DATA = 'path/39.Datalog.2013.02.20.04.14.20.datalog.txt'
BOT_LOG = 'path/56.TweeBotLog.2013.02.20.08.55.15.txt'
BOT_STATS = 'path/11.TweeBotStats.txt'
BOT_FOCUS = 'path/focussingstage.fullfocus12.focustable.txt'
BOT_SCRIPT = 'path/1.SavedTweeBotScript.2013.02.19.17.04.25.whole.groovy'
BOT_CCD = 'path/5.Snapshot..2013.02.19.18.26.16.584.ccd.png'
BOT_ANDOR = 'path/1.Snapshot..2013.02.16.16.12.14.405.andor.png'

BOT_FILES = namedtuple('BOT_FILES', ['data', 'log', 'stats', 'focus', 'script', 'ccd', 'andor'])
bot = BOT_FILES(BOT_DATA, BOT_LOG, BOT_STATS, BOT_FOCUS, BOT_SCRIPT, BOT_CCD, BOT_ANDOR)

# Valid Manual Tweezer Files
MAN_DATA = ['data/2_c.txt', 'data/5.txt', 'data/23_c.txt']

MAN_PM_DIST_CAL_RES = 'path/PM_calibration_calib_pm2pix.txt'
MAN_PM_DIST_CAL_MAT = 'path/PM_calibration_pm2p.txt'
MAN_PM_DIST_CAL_VID = 'path/PM_calibration_video.avi'

MAN_AOD_DIST_CAL_RES = 'path/AOD_calibration_calib_aod2pix.txt'
MAN_AOD_DIST_CAL_MAT = 'path/AOD_calibration_aod2p.txt'
MAN_AOD_DIST_CAL_VID = 'path/AOD_calibration_video.avi'

MAN_DIST_CAL_TMP = 'path/calibration_template_db_tb.tif'

# Valid files for both tweezer modes (e.g. thermal calibration)
TC_PSD = ['path/PSD_4_d.txt', 'path/PSD_5.txt', 'path/PSD_10.txt']
TC_TS = ['path/TS_4_d.txt', 'path/TS_5.txt', 'path/TS_10.txt']

MAN_FILES = namedtuple('MAN_FILES', ['data', 'pm_dist_cal_res', 'pm_dist_cal_mat', 'pm_dist_cal_vid','dist_cal_temp', 'aod_dist_cal_res', 'aod_dist_cal_mat', 'aod_dist_cal_vid'])

man = MAN_FILES(MAN_DATA, MAN_PM_DIST_CAL_RES, MAN_PM_DIST_CAL_MAT, MAN_PM_DIST_CAL_VID, MAN_DIST_CAL_TMP, MAN_AOD_DIST_CAL_RES, MAN_AOD_DIST_CAL_MAT, MAN_AOD_DIST_CAL_VID)

def test_tweebot_files():
    # infer valid files correctly
    classify(bot.data).should.equal('BOT_DATA') 
    classify(bot.log).should.equal('BOT_LOG') 
    classify(bot.stats).should.equal('BOT_STATS') 
    classify(bot.focus).should.equal('BOT_FOCUS') 
    classify(bot.script).should.equal('BOT_SCRIPT') 
    classify(bot.ccd).should.equal('BOT_CCD') 
    classify(bot.andor).should.equal('BOT_ANDOR') 

    # don't get confused on files that are not valid
    classify(bot.log).shouldnot.equal('BOT_DATA') 
    classify(bot.stats).shouldnot.equal('BOT_DATA') 
    classify(bot.focus).shouldnot.equal('BOT_DATA') 
    classify('path/tst.t').shouldnot.equal('BOT_DATA') 
    # classify(man.data).shouldnot.equal('BOT_DATA') 


def test_manunal_files():
    # infer valid files correctly
    classify(man.data[0]).should.equal('MAN_DATA')
    classify(man.data[1]).should.equal('MAN_DATA')
    classify(man.data[2]).should.equal('MAN_DATA')

    classify(man.pm_dist_cal_res).should.equal('MAN_PM_DIST_CAL_RES')
    classify(man.pm_dist_cal_mat).should.equal('MAN_PM_DIST_CAL_MAT')
    classify(man.pm_dist_cal_vid).should.equal('MAN_PM_DIST_CAL_VID')

    classify(man.aod_dist_cal_res).should.equal('MAN_AOD_DIST_CAL_RES')
    classify(man.aod_dist_cal_mat).should.equal('MAN_AOD_DIST_CAL_MAT')
    classify(man.aod_dist_cal_vid).should.equal('MAN_AOD_DIST_CAL_VID')

    # classify(man.dist_cal_temp).should.equal('MAN_DIST_CAL_TMP')
