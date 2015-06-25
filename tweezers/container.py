import logging as log
import copy
import pandas as pd

from ixo.decorators import lazy
from tweezers.analysis.psd import PsdComputation, PsdFit
from tweezers.analysis.thermal_calibration import thermalCalibration
from tweezers.meta import MetaDict, UnitDict


class TweezersData():
    """
    TweezersData structure for tweezers experiment data and metadata. It requires a data source object that provides certain
    methods That populate the properties of this class. Note that not all of these methods must be implemented,
    depending of your usage of the class. However, if your data source does not implement a certain method, the code
    will fail only when the according property is called since all of them are evaluated lazily.

    Currently supported properties that require a specific method in the data source:

        ============ ================================== ===================================
        property     required method in data source     data type
        ============ ================================== ===================================
        meta         getMetadata                       :class:`tweezers.MetaDict`
        units        getMetadata                       :class:`tweezers.UnitDict`
        data         getData                           :class:`pandas.DataFrame`
        psdSource    getPsd                            :class:`pandas.DataFrame`
        ts           getTs                             :class:`pandas.DataFrame`
        ============ ================================== ===================================

    The properties require standardized keys for some fields. Additional fields can be present but the ones listed
    here must have the specified names (really? rethink!).

        =============== =============================================================================================
        property        standardized keys
        =============== =============================================================================================
        meta / units    TODO
        data            ``PMxdiff``, ``PMydiff``, ``AODxdiff``, ``AODydiff``
        psdSource / psd ``f``, ``PMx``, ``PMy``, ``AODx``, ``AODy``, ``fitPMx``, ``fitPMy``, ``fitAODx``, ``fitAODy``
        ts              ``PMxdiff``, ``PMydiff``, ``AODxdiff``, ``AODydiff``
        =============== =============================================================================================
    """

    # this variable should be set to false when the object was copied due to data-changing actions (computePsd...)
    original = True

    def __init__(self, dataSource=None, verbose=True):
        """
        Constructor for Data

        Args:
            dataSource: a data source object like e.g. :class:`tweezers.io.source.TxtMpiSource`
            verbose (bool): set the level of verbosity
        """

        # store dataSource object
        if dataSource:
            self.dataSource = dataSource
        else:
            self.dataSource = None
            self.meta = MetaDict()
            self.units = UnitDict()

        # the basicConfig is not working in iPython notebooks :(
        # log.basicConfig(format='%(asctime)s %(levelname)s %(message)s')
        logger = log.getLogger()
        if verbose:
            logger.setLevel(log.INFO)
        else:
            logger.setLevel(log.WARNING)

    @lazy
    def meta(self):
        """
        Attribute that holds the metadata of the experiment. It is evaluated lazily thus the metadata is read only
        when required.

        Returns:
            :class:`tweezers.MetaDict`
        """

        log.info('Reading metadata from data source.')
        meta, units = self.dataSource.getMetadata()
        self.units = units
        return meta

    @lazy
    def units(self):
        """
        Attribute that holds the units to the corresponding meta data. This should be returned by the data source's
        ``getMetadata`` method as well. Evaluated lazily.

        Returns:
            :class:`tweezers.UnitDict`
        """

        meta, units = self.dataSource.getMetadata()
        self.meta = meta
        return units


    @lazy
    def data(self):
        """
        Attribute that holds the experiment data. It is evaluated lazily thus the data is read only when required.

        Returns:
            :class:`pandas.DataFrame`
        """

        log.info('Reading data from data source.')
        return self.dataSource.getData()

    @lazy
    def ts(self):
        """
        Attribute to hold the time series used for the thermal calibration. Evaluated lazily.

        Returns:
            :class:`pandas.DataFrame`
        """

        log.info('Reading timeseries from data source.')
        return self.dataSource.getTs()

    @lazy
    def psd(self):
        """
        Attribute to hold the power spectrum density. If called before :meth:`tweezers.Data.computePsd`,
        it holds the PSD from the data source, otherwise the newly computed one.
        """

        log.info('Reading PSD from data source.')
        return self.dataSource.getPsd()

    def computePsd(self, **kwargs):
        """
        Compute the power spectrum density from the experiments time series which is stored in the ``ts`` attribute.
        All arguments are forwarded to :class:`tweezers.psd.PsdComputation`.
        This method returns a copy of the initial :class:`tweezers.TweezersData` object to prevent e.g. overwriting of
        data that was read from files.

        Returns:
            :class:`tweezers.TweezersData`
        """

        # use the timeseries sampling rate as default if none is given as user input (in kwargs)
        args = {'samplingRate': self.meta['psdSamplingRate']}
        args.update(kwargs)

        psdObj = PsdComputation(self.ts, **args)
        psdMeta, psd = psdObj.psd()

        # create copy
        td = copy.deepcopy(self)

        # store PSD in 'psd' attribute of this object
        td.psd = psd
        # store PSD units
        td.units['psd'] = self.units['timeseries'] + '² / Hz'
        # store psd metadata
        td.meta.update(psdMeta)
        return td

    @lazy
    def psdFit(self):
        """
        Attribute to hold the Lorentzian fit to the power spectrum density. If called before
        :meth:`tweezers.Data.fit_psd`, it holds the fit from the datas ource, otherwise the newly computed one.
        """

        log.info('Reading PSD fit from data source.')
        return self.dataSource.getPsdFit()

    def fitPsd(self, **kwargs):
        """
        Fits the PSD. All input is forwarded to the :class:`tweezers.analysis.psd.PsdFit` object.
        This method returns a copy of the initial :class:`tweezers.TweezersData` object to prevent e.g. overwriting of
        data that was read from files.

        Returns:
            :class:`tweezers.TweezersData`
        """

        # create copy that will be returned
        td = copy.deepcopy(self)

        psdFitObj = PsdFit(td.psd, **kwargs)
        fitParams, psdFit = psdFitObj.fit()
        td.meta.update(fitParams)
        setattr(td, 'psdFit', psdFit)
        return td

    def thermalCalibration(self):
        """
        Perform a thermal calibration. Requires :meth:`tweezers.TweezersData.psd` and
        :meth:`tweezers.TweezersData.psdFit`.

        Returns:
            :class:`tweezers.TweezersData`
        """

        # get axes
        axes = self.meta.subDictKeys()

        for ax in axes:
            # convert radius to nm (likely given in µm)
            if self.units[ax]['beadRadius'] is 'nm':
                radius = self.meta[ax]['beadRadius']
            else:
                radius = self.meta[ax]['beadRadius'] * 1000

            res, units = thermalCalibration(diffCoeff=self.meta[ax]['diffusionCoefficient'],
                                            cornerFreq=self.meta[ax]['cornerFrequency'],
                                            viscosity=self.meta['viscosity'],
                                            beadRadius=radius,
                                            temperature=self.meta['temperature'])

            self.meta.update({ax: res})
            self.units.update({ax: units})
        return self

    def getFacets(self, data, colName='Value', meta=[]):
        """
        Returns a :class:`pandas.DataFrame` suitable for a :class:`seaborn.FacetGrid`, i.e. the axis of a value is
        specified in an extra column instead of having one column per axis.

        Args:
            data (:class:`pandas.DataFrame`): input data
            colName (str): column name of the "value" column
            meta (list): list of strings, the metadata is searched for these keys and they are added as additional
                         columns if available

        Returns:
            :class:`pandas.DataFrame`
        """

        # in case we have frequency or time data, keep that as index
        index = []
        if 'f' in data.columns:
            index = ['f']
        elif 't' in data.columns:
            index = ['t']

        resDf = pd.DataFrame()
        for col in data.columns:
            # skip index columns
            if col in index:
                continue

            tmpDf = data[index + [col]].rename(columns={col: colName})
            tmpDf.loc[:, 'Axis'] = col

            for m in meta:
                if m in self.meta[col].keys():
                    tmpDf.loc[:, m] = self.meta[col][m]
            resDf = resDf.append(tmpDf)

        for m in meta:
            if m in self.meta.keys():
                resDf.loc[:, m] = self.meta[m]

        return resDf