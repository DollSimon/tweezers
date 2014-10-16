# coding=utf-8

import os
import random

import pytest

from tweezer.legacy.cli.utils import list_tweezer_files


@pytest.fixture
def cleanDataDir(tmpdir, request):

    dataDir = tmpdir.mkdir('data')
    calDir = tmpdir.mkdir('thermal_calibration')

    makeData = lambda x: "".join([str(x), "_", random.choice('cd'), ".txt"])
    makePsd = lambda x: "".join(["PSD_", str(x), "_", random.choice('cd'), ".txt"])
    makeTs = lambda x: "".join(["TS_", str(x), "_", random.choice('cd'), ".txt"])

    allFiles = [[makeData(i), makePsd(i), makeTs(i)] for i in range(1, 9)]
    data = [row[0] for row in allFiles]
    psd = [row[1] for row in allFiles]
    ts = [row[2] for row in allFiles]

    dataFiles = [os.path.join([tmpdir, "data", f]) for f in data]
    psdFiles = [os.path.join([tmpdir, "thermal_calibration", f]) for f in psd]
    tsFiles = [os.path.join([tmpdir, "thermal_calibration", f]) for f in ts]

    return [tmpdir, dataFiles, psdFiles, tsFiles]


def test_is_trial_complete(cleanDataDir):
    print("Temporary directory: ", cleanDataDir[2])
    files = list_tweezer_files(cleanDataDir[0])
    assert 'man_data' in files
    assert 'tc_psd' in files
    assert 'tc_ts' in files

