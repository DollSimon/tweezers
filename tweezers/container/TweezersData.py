import copy
import logging as log
from collections import OrderedDict
import pandas as pd

from tweezers.analysis.psd import PsdComputation, PsdFit
from tweezers.analysis.thermal_calibration import thermalCalibration
from tweezers.container.TweezersAnalysis import TweezersAnalysis
from tweezers.ixo.collections import IndexedOrderedDict
from tweezers.ixo.decorators import lazy
from tweezers.ixo.statistics import averageData
from tweezers.meta import MetaDict, UnitDict
from tweezers.plot.psd import PsdFitPlot
from tweezers.plot.utils import peekPlot


class TweezersDataBase:
    """
    Base class for storing tweezers data. This class should implement methods and attributes that both,
    the :class:`.TweezersData` and the :class:`.TweezersDataSegment` require.

    The following attributes are populated lazily on the first call.

    Attributes:
        meta (:class:`.MetaDict`):          metadata of the experiment
        units (:class:`.UnitDict`):         units of the metadata
        psd (:class:`pandas.DataFrame`):    power spectrum data
        psdFit (:class:`pandas.DataFrame`): power spectrum fit data
        ts (:class:`pandas.DataFrame`):     time series for thermal calibration
    """

    @lazy
    def meta(self):
        """
        Attribute that holds the metadata of the experiment. It is evaluated lazily thus the metadata is read only
        when required.

        Returns:
            :class:`.MetaDict`
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
            :class:`.UnitDict`
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
        Attribute to hold the power spectrum density. If called before :meth:`.computePsd`,
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
            nsamples (`int`): number of samples to average

        Returns:
            :class:`pandas.DataFrame`
        """

        return averageData(self.data, nsamples=nsamples)

    def computePsd(self, **kwargs):
        """
        Compute the power spectrum density from the experiments time series which is stored in the ``ts`` attribute.
        All arguments are forwarded to :class:`.PsdComputation`.
        This method returns a copy of the initial :class:`.TweezersData` object to prevent e.g. overwriting of
        data that was read from files.

        Returns:
            :class:`.TweezersData`
        """

        # use the timeseries sampling rate as default if none is given as user input (in kwargs)
        args = {'samplingRate': self.meta['psdSamplingRate']}
        args.update(kwargs)

        psdObj = PsdComputation(self.ts, **kwargs)
        psdMeta, psd = psdObj.psd()

        # create copy
        td = self.copy()

        # store PSD in 'psd' attribute of this object
        td.psd = psd
        # store PSD units
        td.units['psd'] = self.units['timeseries'] + '^2/Hz'
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
        :meth:`.fit_psd`, it holds the fit from the data source, otherwise the newly computed one.
        """

        log.debug('Reading PSD fit from data source.')
        return self.source.getPsdFit()

    def fitPsd(self, **kwargs):
        """
        Fits the PSD. All input is forwarded to the :class:`.PsdFit` object.
        This method returns a copy of the initial :class:`.TweezersData` object to prevent e.g. overwriting of
        data that was read from files.

        Returns:
            :class:`.TweezersData`
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
        Perform a thermal calibration. Requires :meth:`.psd` and
        :meth:`.psdFit`.
        Returns a copy of the initial object.

        Returns:
            :class:`.TweezersData`
        """

        t = self.copy()

        for ax in t.meta.traps:
            # convert diameter to nm (likely given in µm)
            if t.units[ax]['beadDiameter'] == 'nm':
                diam = t.meta[ax]['beadDiameter']
            elif t.units[ax]['beadDiameter'] in ['um', 'µm']:
                diam = t.meta[ax]['beadDiameter'] * 1000
            else:
                raise ValueError('Unknown bead radius unit encountered.')

            res, units = thermalCalibration(diffCoeff=t.meta[ax]['diffusionCoefficient'],
                                            cornerFreq=t.meta[ax]['cornerFrequency'],
                                            viscosity=t.meta['viscosity'],
                                            beadDiameter=diam,
                                            temperature=t.meta['temperature'])

            t.meta.update({ax: res})
            t.units.update({ax: units})

        # recompute forces
        t.meta, t.units, t.data = t.source.calculateForce(t.meta, t.units, t.data)

        return t

    def copy(self):
        """
        Returns a deep copy of the object

        Args:


        Returns:
            :class:`.TweezersDataBase`
        """

        return copy.deepcopy(self)

    def getFacets(self, data, colName='Value', meta=[]):
        """
        Returns a :class:`pandas.DataFrame` suitable for a :class:`seaborn.FacetGrid`, i.e. the axis of a value is
        specified in an extra column instead of having one column per axis.

        Args:
            data (:class:`pandas.DataFrame`): input data
            colName (`str`): column name of the "value" column
            meta (`list` of `str`): list of strings, the metadata is searched for these keys and they are added as
                additional columns if available

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
        """
        Show a :func:`.peekPlot` of the current data.

        Args:
            *cols: see :func:`.peekPlot`

        Returns:
            :class:`.TweezersData`
        """

        peekPlot(self, *cols)
        return self

    def peekPsd(self):
        """
        Plots the PSD, see :class:`.PsdFitPlot`

        Returns:
            :class:`.TweezersData`
        """

        PsdFitPlot(self, residuals=False)
        return self

    def getAnalysis(self, path, name=None):
        """
        Convert the current :class:`.TweezersData` to a :class:`.TweezersAnalysis`, the general format to store and
        exchange analysis results.

        Args:
            path (`str`): path to the directory that will hold the :class:`tweezers.TweezersAnalysis` file
            name (`str`, optional): name for the analysis file, constructed from metadata if not given (using the ID)

        Returns:
            :class:`.TweezersAnalysis`
        """

        analysis = self.getEmptyAnalysis(path, name=name)
        analysis.data = copy.deepcopy(self.data)
        return analysis

    def getSegmentAnalysis(self, path, name=None):
        """
        Convert all segments of the current :class:`.TweezersData` to a :class:`.TweezersAnalysis`, the general
        format to store and exchange analysis results.

        Args:
            path (`str`): path to the directory that will hold the :class:`tweezers.TweezersAnalysis` file
            name (`str`, optional): name for the analysis file, constructed from metadata if not given (using the ID)

        Returns:
            :class:`.TweezersAnalysis` or `None` if no segments are defined
        """

        # if there are no segments, ignore this dataset
        if not self.segments:
            return None

        analysis = self.getEmptyAnalysis(path, name=name)
        analysis.addField('segments')
        for key in self.segments.keys():
            seg = self.getSegment(key)
            analysis.segments[key] = IndexedOrderedDict(data=seg.data, id=seg.meta.id, idSafe=seg.meta.idSafe)
        return analysis

    def getEmptyAnalysis(self, path, name=None):
        """
        Shared code that prepares export of an analysis file, used by :meth:`.getAnalysis` and
        :meth:`.getSegmentAnalysis`.

        Args:
            path: see :meth:`.getAnalysis`
            name: see :meth:`.getAnalysis`

        Returns:
            :class:`.TweezersAnalysis`
        """

        if not name:
            name = self.meta.id
        name = TweezersAnalysis.getFilename(name)

        analysis = TweezersAnalysis(path=path, name=name)
        analysis.meta = copy.deepcopy(self.meta)
        analysis.units = copy.deepcopy(self.units)
        analysis.meta['sourceClass'] = self.source.__class__.__name__
        return analysis


class TweezersData(TweezersDataBase):
    """
    TweezersData structure for tweezers experiment data and metadata. It requires a data source object that
    implements the methods of :class:`.BaseSource` to populate its properties.
    Note that not all of these methods must be implemented, depending of your usage of the class. However, if
    your data source does not implement a certain method, the code
    will fail only when the according property is called since all of them are evaluated lazily.


    Attributes:
        data (:class:`pandas.DataFrame`):               experimental data
        analysis (:class:`collections.OrderedDict`):    storage for analysis results
        segments (:class:`.IndexedOrderedDict`):        segment data
    """

    def __init__(self, source=None):
        """
        Args:
            source (:class:`.BaseSource`): a data source object like e.g. :class:`.TxtBiotecSource`
        """

        super().__init__()
        # store dataSource object
        if source:
            self.source = source
        else:
            self.source = None
            self.meta = MetaDict()
            self.units = UnitDict()
        # ToDo: check:
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

    def addSegment(self, tmin, tmax, name=None):
        """
        Add a segment with the given limits.

        Args:
            tmin (`float`): relative starting time of the segment
            tmax (`float`): relative end time of the segment
            name (`str`, optional): name (ID) of the segment, defaults to ``int(tmin)``

        Returns:
            :class:`.TweezersData`
        """

        # create a standard name if none is given
        if not name:
            # converting to integer seconds might cause clashes, better option?
            name = '{:.0f}'.format(tmin)
            if name in self.segments.keys():
                log.warning('Segment key "{}" is being overridden'.format(name))

        # insert segment
        self.segments[name] = IndexedOrderedDict([('tmin', tmin), ('tmax', tmax)])
        # sort segments by name
        self.segments = self.segments.sorted()

        return self

    def deleteSegment(self, segId):
        """
        Delete the segment with the given name or numeric index.

        Args:
            segId (`int` or `str`): name or numeric index of the segment to delete

        Returns:
            :class:`.TweezersData`
        """

        self.segments.pop(segId)
        return self

    def getSegment(self, segId):
        """
        Returns the segment with the given name or numeric index.

        Args:
            segId (`int` or `str`): name or numeric index of the segment to return

        Returns:
            :class:`.TweezersDataSegment`
        """

        # check if segments are available
        if not self.segments:
            raise KeyError('No segments defined')

        return TweezersDataSegment(self, segId)


class TweezersDataSegment(TweezersDataBase):
    """
    Class to hold the data of a data segment. Can be used in the same way as :class:`.TweezersData`.

    Attributes:
        data (:class:`pandas.DataFrame`):               experimental data
        analysis (:class:`collections.OrderedDict`):    storage for analysis results
    """

    def __init__(self, tdInstance, segmentId):
        """
        Args:
            tdInstance (:class:`.TweezersData`): instance to get the segment from
            segmentId (`int` or `str`): name or numeric index of the segment to return
        """

        super().__init__()
        self.__dict__ = copy.deepcopy(tdInstance.__dict__)
        # get the proper key in case numeric indexing was used
        segmentId = self.segments.key(segmentId)
        self.segment = self.segments[segmentId]
        # get rid of the other segments
        del self.segments
        # update meta dict
        self.meta['segment'] = segmentId
        self.meta['id'] = '{} - {}'.format(self.meta['id'], segmentId)
        self.meta['idSafe'] = self.meta['id'].replace('_', ' ').replace('#', '')

        # check if data is already read into memory and use that if available
        if 'data' in self.__dict__:
            # adjust data
            queryStr = '{} <= time <= {}'.format(self.segment['tmin'], self.segment['tmax'])
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
        data = self.source.getDataSegment(self.segment['tmin'], self.segment['tmax'])
        self.meta, self.units, data = self.source.postprocessData(self.meta, self.units, data)
        return data
