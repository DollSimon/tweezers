from tweezer.io.source import TxtSourceMpi
from tweezer.container import Data
# from tweezer.analysis.psd import PsdAnalysis
# import tweezer.container as c
from ixo import utils
from tweezer.plot.psd import PsdPlot

# path = '/Users/christophehrlich/Documents/TranscriptionData/test_data/data/35_Date_2014_08_18_15_55_29_JSON.txt'
pathData = '/Users/christophehrlich/Documents/TranscriptionData/test_data/data/35_Date_2014_08_18_15_55_29.txt'
pathPSD = '/Users/christophehrlich/Documents/TranscriptionData/test_data/thermal_calibration/PSD_35_Date_2014_08_18_15_55_29.txt'
pathTS = '/Users/christophehrlich/Documents/TranscriptionData/test_data/thermal_calibration/TS_35_Date_2014_08_18_15_55_29.txt'
source = TxtSourceMpi(data=pathData, psd=pathPSD, ts=pathTS)
# header, column, data = source.read_file()
data = Data(source)
data = data.fit_psd()
psdPlot = PsdPlot(data)
# psd = PsdAnalysis(data)
# psd.fit()
# psdPlot = PsdPlot(data)
