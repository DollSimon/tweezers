import copy
import logging as log
from collections import OrderedDict
import pandas as pd
import numpy as np

from tweezers.container.TweezersAnalysis import TweezersAnalysis
from tweezers.ixo.collections import IndexedOrderedDict
from tweezers.ixo.decorators import lazy
from tweezers.ixo.statistics import averageDf
from tweezers.meta import MetaDict, UnitDict
from tweezers.plot.psd import PsdFitPlot
from tweezers.plot.utils import peekPlot
import tweezers.calibration.psd as psd
import tweezers.calibration.thermal as thermal
from tweezers.physics.tweezers import tcOsciHydroCorrect


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

        return averageDf(self.data, nsamples=nsamples)

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

        # create copy
        t = self.copy()

        data = {}
        cols = ['f']
        # compute PSD for each trap
        for trap in t.meta.traps:
            psdTrap = psd.computePsd(t.ts[trap], **kwargs)[0]
            data[trap] = psdTrap['psdMean']
            data[trap + 'Std'] = psdTrap['psdStd']
            cols += [trap, trap + 'Std']
        data['f'] = psdTrap['f']

        # store PSD
        t.psd = pd.DataFrame(data, columns=cols)
        # store PSD metadata
        t.meta['psdBlockLength'] = psdTrap['blockLength']
        t.meta['psdNBlocks'] = psdTrap['nBlocks']
        t.meta['psdOverlap'] = psdTrap['overlap']

        # store PSD units
        t.units['psd'] = t.units['timeseries'] + '^2/Hz'

        # delete PSD fit and thermal calibration data if present to prevent confusion with newly computed PSD and old fits
        t.psdFit = None
        t.meta.deleteKey('diffusionCoefficient', 'cornerFrequency', 'psdFitError', 'psdFitR2', 'psdFitChi2',
                         'displacementSensitivity', 'forceSensitivity', 'stiffness')
        t.units.deleteKey('diffusionCoefficient', 'cornerFrequency', 'psdFitError', 'psdFitR2', 'psdFitChi2',
                          'displacementSensitivity', 'forceSensitivity', 'stiffness')

        return t

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
        t = self.copy()

        data = {}
        cols = ['f'] + t.meta.traps
        # fit PSD for each trap
        for trap in t.meta.traps:
            # check for oscillation calibration to exclude peak from fitting
            peakF = 0
            if t.meta.psdType == 'oscillation':
                peakF = t.meta.psdOscillateFrequency
            # fit psd
            fitTrap = psd.PsdFit(t.psd.f, t.psd[trap], std=t.psd[trap + 'Std'], peakF=peakF, **kwargs)
            # store fit function data
            data[trap] = fitTrap.yFitFull
            # store fit result parameters
            t.meta[trap].update(fitTrap.fitresAsMeta())
        data['f'] = fitTrap.fFull

        # store PSD fit
        t.psdFit = pd.DataFrame(data, columns=cols)
        # store extra metadata
        t.meta['psdFitMinF'] = data['f'].iloc[0]
        t.meta['psdFitMaxF'] = data['f'].iloc[-1]

        return t

    def thermalCalibration(self):
        """
        Perform a thermal calibration. Requires :meth:`.psd` and
        :meth:`.psdFit`.
        Returns a copy of the initial object.

        Returns:
            :class:`.TweezersData`
        """

        t = self.copy()

        # sort traps such that y-traps are calibrated first, required for oscillation calibration (gets dragCoef from
        # y and uses that for x
        trapsSorted = sorted(t.meta.traps, key=lambda s: s[-1], reverse=True)
        for trap in trapsSorted:
            thermal.doThermalCalib(t, trap)

        # recompute forces
        t.meta, t.units, t.data = t.source.calculateForce(t.meta, t.units, t.data)

        return t

    def osciHydroCorr(self):
        """
        Correct results of thermal calibration performed with oscillation technique.

        Returns a copy of the initial object.

        Returns:
            :class:`.TweezersData`
        """

        t = self.copy()
        m = t.meta
        # radii in nm
        rPm = m.pmY.beadDiameter / 2 * 1000
        rAod = m.aodY.beadDiameter / 2 * 1000

        # get y distance
        dy = np.abs(m.pmY.trapPosition - m.aodY.trapPosition)

        # todo correct x-axis parameters?
        # go through y-traps
        for trap in m.traps:
            if not trap.lower().endswith('y'):
                continue
            # the radius in the equation is that of the other bead (that causes the flow field)
            [rTrap, rOther] = [rPm, rAod] if trap.lower().startswith('pm') else [rAod, rPm]
            # get correction factor
            c = tcOsciHydroCorrect(dy, rTrap=rTrap, rOther=rOther, method='oseen')
            # store correction factor
            m[trap]['hydroCorr'] = c
            # also store for x-trap
            xTrap = trap[:-1] + 'X'
            m[xTrap]['hydroCorr'] = c

            # correct the calibration parameters
        for trap in m.traps:
            c = m[trap].hydroCorr
            m[trap].displacementSensitivity *= c
            m[trap].stiffness /= c ** 2
            m[trap].forceSensitivity /= c

        # recompute data
        t.meta, t.units, t.data = t.source.postprocessData(m, t.units, t.data)

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

    def getAnalysis(self, name=None):
        """
        Convert the current :class:`.TweezersData` to a :class:`.TweezersAnalysis`, the general format to store and
        exchange analysis results.

        Args:
            name (`str`, optional): name for the analysis file, constructed from metadata if not given (using the ID)

        Returns:
            :class:`.TweezersAnalysis`
        """

        analysis = self.getEmptyAnalysis(name=name)
        analysis.data = copy.deepcopy(self.data)
        return analysis

    def getSegmentAnalysis(self, name=None):
        """
        Convert all segments of the current :class:`.TweezersData` to a :class:`.TweezersAnalysis`, the general
        format to store and exchange analysis results.

        Args:
            name (`str`, optional): name for the analysis file, constructed from metadata if not given (using the ID)

        Returns:
            :class:`.TweezersAnalysis` or `None` if no segments are defined
        """

        # if there are no segments, ignore this dataset
        if not self.segments:
            return None

        analysis = self.getEmptyAnalysis(name=name)
        analysis.addField('segments')
        for key in self.segments.keys():
            seg = self.getSegment(key)
            analysis.segments[key] = IndexedOrderedDict(data=seg.data, id=seg.meta.id, idSafe=seg.meta.idSafe)
        return analysis

    def getEmptyAnalysis(self, name=None):
        """
        Shared code that prepares export of an analysis file, used by :meth:`.getAnalysis` and
        :meth:`.getSegmentAnalysis`.

        Args:
            name: see :meth:`.getAnalysis`

        Returns:
            :class:`.TweezersAnalysis`
        """

        if not name:
            name = self.meta.id
        name = TweezersAnalysis.getFilename(name)

        analysis = TweezersAnalysis(name=name)
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
