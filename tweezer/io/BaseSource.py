class BaseSource():
    """
    Base class for data sources. Inherit from this class when creating a new data source. Keep in mind that not all
    methods described here must be implemented since they are only called when the associated property of the
    :class:`tweezer.TweezerData` object is requested, depending on your analysis.

    Keep in mind that this object should not hold the actual data but rather be an standardized interface to `get`
    the data from wherever it is. This allows the :class:`tweezer.TweezerData` to lazily load the data only when
    required.
    """

    def get_metadata(self):
        """
        Returns the metadata of the experiment.

        Returns:
            :class:`tweezer.MetaDict` and :class:`tweezer.UnitDict`
        """

        raise NotImplementedError()

    def get_data(self):
        """
        Returns the experiment data.

        Returns:
            :class:`pandas.DataFrame`
        """

        raise NotImplementedError()

    def get_psd(self):
        """
        Returns the power spectral density (PSD) used for the calibration of the experiment by the data source.

        Args:


        Returns:
            :class:`pandas.DataFrame`
        """

        raise NotImplementedError()

    def get_ts(self):
        """
        Returns the time series recorded for the thermal calibration of the experiment. This is used to compute the
        PSD.

        Returns:
            :class:`pandas.DataFrame`
        """

        raise NotImplementedError()