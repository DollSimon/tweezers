import json

from tweezers.ixo.collections import IndexedOrderedDict
from tweezers.ixo.io import DataFrameJsonDecoder, DataFrameJsonEncoder


class BaseSource:
    """
    Base class for data sources. Inherit from this class when creating a new data source. Keep in mind that not all
    methods described here must be implemented since they are only called when the associated property of the
    :class:`tweezers.TweezersData` object is requested, depending on your analysis.

    Keep in mind that this object should not hold the actual data but rather be an standardized interface to `get`
    the data from wherever it is. This allows the :class:`tweezers.TweezersData` to lazily load the data only when
    required.
    """

    analysis = None

    def __init__(self, **kwargs):
        pass

    def getMetadata(self):
        """
        Returns the metadata of the experiment.

        Returns:
            :class:`tweezers.MetaDict` and :class:`tweezers.UnitDict`
        """

        raise NotImplementedError()

    def getData(self):
        """
        Returns the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        raise NotImplementedError()

    def getDataSegment(self, tmin, tmax, chunkN=10000):
        """
        Returns the data between ``tmin`` and ``tmax``.

        Args:
            tmin (float): minimum data timestamp
            tmax (float): maximum data timestamp
            chunkN (int): number of rows to read per chunk

        Returns:
            :class:`pandas.DataFrame`
        """

        raise NotImplementedError()

    def getPsd(self):
        """
        Returns the power spectral density (PSD) used for the calibration of the experiment by the data source.

        Returns:
            :class:`pandas.DataFrame`
        """

        raise NotImplementedError()

    def getTs(self):
        """
        Returns the time series recorded for the thermal calibration of the experiment. This is used to compute the
        PSD.

        Returns:
            :class:`pandas.DataFrame`
        """

        raise NotImplementedError()

    def getPsdFit(self):
        """
        Returns the fit to the PSD as performed by the data source.

        Returns:
            :class:`pandas.DataFrame`
        """

        raise NotImplementedError()

    def postprocessData(self, meta, units, data):
        """
        This method is run after importing the data and can be used to modify the data and metadata or units.

        Args:
            meta (:class:`tweezers.MetaDict`): :class:`tweezers.MetaDict`
            units: :class:`tweezers.UnitDict`
            data: :class:`pandas.DataFrame`

        Returns:
            meta, units, data
        """

        return meta, units, data

    def getAnalysisFile(self):
        """
        Create the analysis file name.

        Returns:
            :class:`pathlib.Path`
        """

        raise NotImplementedError()

    def readAnalysisFile(self):
        """
        Read the content of the analysis file from disk.

        Returns:
            :class:`tweezers.ixo.utils.IndexedOrderedDict`
        """

        if not self.analysis:
            return IndexedOrderedDict()

        with self.analysis.open(mode='r', encoding='utf-8') as f:
            analysisDict = json.load(f, object_pairs_hook=IndexedOrderedDict, cls=DataFrameJsonDecoder)
        return analysisDict

    def writeAnalysisFile(self, analysisDict):
        """
        Write the analysis file to disk.

        Args:
            analysisDict (:class:`tweezers.ixo.utils.IndexedOrderedDict`): analysis dictionary
        """

        # build filename if it does not exist
        if not self.analysis:
            self.analysis = self.getAnalysisFile()

        # write data to file
        jsonStr = json.dumps(analysisDict, indent=4, cls=DataFrameJsonEncoder)
        with self.analysis.open(mode='w', encoding='utf-8') as f:
            f.write(jsonStr)

    def getAnalysis(self):
        """
        Return the analysis data.

        Returns:
            :class:`collections.OrderedDict`
        """

        return self.readAnalysisFile().get('analysis', IndexedOrderedDict())

    def writeAnalysis(self, analysis, segment=None):
        """
        Write the analysis data back to disk.

        Args:
            analysis (:class:`collections.OrderedDict`): the analysis data to store
        """

        analysisDict = self.readAnalysisFile()

        # should we only update the segment?
        if segment is not None:
            analysisDict['segments'][segment] = analysis
            # remove the general analysis keys
            for key in analysisDict['analysis'].keys():
                analysisDict['segments'][segment].pop(key, None)
        else:
            # sort analysis keys and store in the proper dictionary
            analysisDict['analysis'] = IndexedOrderedDict(sorted(analysis.items()))

        self.writeAnalysisFile(analysisDict)

    def getSegments(self):
        """
        Return a list of all segments.

        Returns:
            :class:`tweezers.ixo.collections.IndexedOrderedDict`
        """

        return self.readAnalysisFile().get('segments', IndexedOrderedDict())

    def writeSegments(self, segments):
        """
        Write segment information back to disk.

        Args:
            segments (:class:`tweezers.ixo.collections.IndexedOrderedDict`): segment dictionary
        """

        analysisDict = self.readAnalysisFile()
        analysisDict['segments'] = segments
        self.writeAnalysisFile(analysisDict)