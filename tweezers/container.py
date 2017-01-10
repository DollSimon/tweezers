import logging as log
import copy
import pandas as pd
from collections import OrderedDict

from tweezers.ixo.decorators import lazy
from tweezers.analysis.psd import PsdComputation, PsdFit
from tweezers.analysis.thermal_calibration import thermalCalibration
from tweezers.meta import MetaDict, UnitDict
from tweezers.plot.utils import peekPlot
from tweezers.plot.psd import PsdFitPlot
from tweezers.ixo.collections import IndexedOrderedDict


class TweezersDataBase:
    # todo: docstring
    # base class for TweezersData and TweezersDataSegment, implement stuff that both should be able to do here

    @lazy
    def meta(self):
        """
        Attribute that holds the metadata of the experiment. It is evaluated lazily thus the metadata is read only
        when required.

        Returns:
            :class:`tweezers.MetaDict`
        """

        log.debug('Reading metadata from data source.')
        meta, units = self.source.getMetadata()
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

        meta, units = self.source.getMetadata()
        self.meta = meta
        return units

    @lazy
    def ts(self):
        """
        Attribute to hold the time series used for the thermal calibration. Evaluated lazily.

        Returns:
            :class:`pandas.DataFrame`
        """

        log.debug('Reading timeseries from data source.')
        return self.source.getTs()

    @lazy
    def psd(self):
        """
        Attribute to hold the power spectrum density. If called before :meth:`tweezers.Data.computePsd`,
        it holds the PSD from the data source, otherwise the newly computed one.
        """

        log.debug('Reading PSD from data source.')
        return self.source.getPsd()

    @property
    def avData(self):
        """
        Attribute to return the default downsampled and averaged data. Evaluated each time the
        attribute is called.
        """

        return self.averageData(nsamples=10)

    def averageData(self, nsamples=10):
        """
        Downsample the data by averaging ``nsamples``.
        Args:
            nsamples (int): number of samples to average

        Returns:
            :class:`tweezers.TweezersData`
        """

        group = self.data.groupby(self.data.index // nsamples)
        avData = group.mean()
        avData['time'] = group.first()['time']
        if 'absTime' in self.data.columns:
            avData['absTime'] = group.first()['absTime']

        return avData

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

        # delete PSD fit and thermal calibration data if present to prevent confusion with newly computed PSD and old fits
        td.psdFit = None
        td.meta.deleteKey('diffusionCoefficient', 'cornerFrequency', 'psdFitError', 'psdFitR2', 'psdFitChi2',
                          'displacementSensitivity', 'forceSensitivity', 'stiffness')
        td.units.deleteKey('diffusionCoefficient', 'cornerFrequency', 'psdFitError', 'psdFitR2', 'psdFitChi2',
                           'displacementSensitivity', 'forceSensitivity', 'stiffness')

        return td

    @lazy
    def psdFit(self):
        """
        Attribute to hold the Lorentzian fit to the power spectrum density. If called before
        :meth:`tweezers.Data.fit_psd`, it holds the fit from the data source, otherwise the newly computed one.
        """

        log.debug('Reading PSD fit from data source.')
        return self.source.getPsdFit()

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
            # convert diameter to nm (likely given in µm)
            if self.units[ax]['beadDiameter'] == 'nm':
                diam = self.meta[ax]['beadDiameter']
            elif self.units[ax]['beadDiameter'] in ['um', 'µm']:
                diam = self.meta[ax]['beadDiameter'] * 1000
            else:
                raise ValueError('Unknown bead radius unit encountered.')

            res, units = thermalCalibration(diffCoeff=self.meta[ax]['diffusionCoefficient'],
                                            cornerFreq=self.meta[ax]['cornerFrequency'],
                                            viscosity=self.meta['viscosity'],
                                            beadDiameter=diam,
                                            temperature=self.meta['temperature'])

            self.meta.update({ax: res})
            self.units.update({ax: units})

        # recompute forces
        self.meta, self.units, self.data = self.source.computeForces(self.meta, self.units, self.data)

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

    def peek(self, *cols):
        # ToDo: docstring
        peekPlot(self, *cols)
        return self

    def peekPsd(self):
        # ToDo: docstring
        PsdFitPlot(self, residuals=False)
        return self


class TweezersData(TweezersDataBase):
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
    # todo rework docstring

    def __init__(self, source=None):
        """
        Constructor for Data

        Args:
            source: a data source object like e.g. :class:`tweezers.io.source.TxtMpiSource`
        """

        super().__init__()
        # store dataSource object
        if source:
            self.source = source
        else:
            self.source = None
            self.meta = MetaDict()
            self.units = UnitDict()
            self.analysis = OrderedDict()
            self.segments = IndexedOrderedDict()

    @lazy
    def data(self):
        """
        Attribute that holds the experiment data. It is evaluated lazily thus the data is read only when required.

        Returns:
            :class:`pandas.DataFrame`
        """

        log.debug('Reading data from data source')
        data = self.source.getData()
        self.meta, self.units, data = self.source.postprocessData(self.meta, self.units, data)
        return data

    @lazy
    def analysis(self):
        """
        Attribute that holds the analysis data, evaluated lazily.

        Returns:
            :class:`collections.OrderedDict`
        """

        log.debug('Reading analysis from data source')
        return self.source.getAnalysis()

    @lazy
    def segments(self):
        # todo docstring

        log.debug('Reading segments from data source')
        return self.source.getSegments()

    def save(self):
        """
        Save the analysis data back to disk.

        Returns:
            :class:`tweezers.TweezersData`
        """
        # todo docstring update

        self.source.writeAnalysis(self.analysis)
        self.source.writeSegments(self.segments)
        return self

    def addSegment(self, tmin, tmax, name=None):
        # ToDo: docstring
        # tmin and tmax are relative times

        # create a standard name if none is given
        if not name:
            # converting to integer seconds might cause clashes, better option?
            name = '{:.0f}'.format(tmin)
            if name in self.segments.keys():
                log.warning('Segment key "{}" is being overridden'.format(name))

        # insert segment
        self.segments[name] = IndexedOrderedDict([('tmin', tmin), ('tmax', tmax)])
        # sort segments by tmin
        self.segments = self.segments.sorted(key=lambda t: t[1]['tmin'])

        return self

    def deleteSegment(self, segId):
        # todo: docstring

        self.segments.pop(segId)
        return self

    def getSegment(self, segId):
        # todo: docstring

        # check if segments are available
        if not self.segments:
            raise KeyError('No segments defined')

        return TweezersDataSegment(self, segId)


class TweezersDataSegment(TweezersDataBase):
    # todo docstring

    def __init__(self, tdInstance, segmentId):
        # todo: docstring
        super().__init__()
        self.__dict__ = copy.deepcopy(tdInstance.__dict__)
        # get the proper key in case numeric indexing was used
        segmentId = self.segments.key(segmentId)
        self.analysis = self.segments[segmentId]
        self.analysis.update(tdInstance.analysis)
        # get rid of the other segments
        del self.segments
        # update meta dict
        self.meta['segment'] = segmentId
        self.meta['id'] = '{} - {}'.format(self.meta['id'], segmentId)

        # check if data is already read into memory and use that if available
        if 'data' in self.__dict__:
            # adjust data
            queryStr = '{} <= absTime <= {}'.format(self.analysis['tmin'], self.analysis['tmax'])
            self.data = self.data.query(queryStr)
            self.data = self.data.reset_index(drop=True)
            self.data.loc[:, 'time'] -= self.data.loc[0, 'time']
            # delete avData if available
            try:
                self.__dict__.pop('avData')
            except KeyError:
                pass

    @lazy
    def data(self):
        """
        Attribute that holds the experiment data. It is evaluated lazily thus the data is read only when required.

        Returns:
            :class:`pandas.DataFrame`
        """

        log.debug('Reading data from data source.')
        data = self.source.getDataSegment(self.analysis['tmin'], self.analysis['tmax'])
        self.meta, self.units, data = self.source.postprocessData(self.meta, self.units, data)
        return data

    def save(self):
        """
        Save the analysis data back to disk.

        Returns:
            :class:`tweezers.TweezersData`
        """

        self.source.writeAnalysis(self.analysis, segment=self.meta['segment'])
        return self
