from pathlib import Path


class BaseSource:
    """
    Base class for data sources. Inherit from this class when creating a new data source. Keep in mind that not all
    methods described here must be implemented since they are only called when the associated property of the
    :class:`tweezers.TweezersData` object is requested, depending on your analysis.

    Keep in mind that this object should not hold the actual data but rather be an standardized interface to `get`
    the data from wherever it is. This allows the :class:`tweezers.TweezersData` to lazily load the data only when
    required.
    """

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

        # default expensive implementation....
        return self.getData().query('{} <= time <= {}'.format(tmin, tmax))


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

    @staticmethod
    def postprocessData(meta, units, data):
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

    def getTime(self):
        """
        Return the time of the source.

        Returns:
            `datetime.datetime`
        """

        raise NotImplementedError()

    @staticmethod
    def calculateForce(meta, units, data):
        """
        Calculate forces from Diff signal and calibration values.

        Args:
            meta (:class:`.MetaDict`): metadata
            units (:class:`.UnitDict`): unit metadata
            data (:class:`pandas.DataFrame`): data

        Returns:

            Updated versions of the input parameters

            * meta (:class:`.MetaDict`)
            * units (:class:`.UnitDict`)
            * data (:class:`pandas.DataFrame`)
        """

        raise NotImplementedError()

    @staticmethod
    def isDataFile(path):

        raise NotImplementedError()

    @classmethod
    def getAllSources(cls, path):

        raise NotImplementedError()

    @classmethod
    def getAllFiles(cls, path):
        """
        Return a recursive list of all valid data files within a given path.

        Args:
            path (:class:`pathlib.Path`): root path to search for valid data files

        Returns:
            `list` of `dict`
        """

        _path = Path(path)
        files = []

        for item in _path.iterdir():
            if item.is_dir():
                subFiles = cls.getAllFiles(item)
                files += subFiles
            else:
                m = cls.isDataFile(item)
                if m:
                    files.append(m)
        return files
