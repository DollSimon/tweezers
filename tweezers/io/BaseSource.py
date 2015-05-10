class BaseSource():
    """
    Base class for data sources. Inherit from this class when creating a new data source. Keep in mind that not all
    methods described here must be implemented since they are only called when the associated property of the
    :class:`tweezers.TweezersData` object is requested, depending on your analysis.

    Keep in mind that this object should not hold the actual data but rather be an standardized interface to `get`
    the data from wherever it is. This allows the :class:`tweezers.TweezersData` to lazily load the data only when
    required.
    """

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