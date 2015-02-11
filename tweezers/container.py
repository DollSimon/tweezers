from ixo.decorators import lazy
from collections import OrderedDict
import pprint
import re
from tweezers.analysis.psd import PsdComputation, PsdFit
import pandas as pd
import logging as log


class MetaBaseDict(OrderedDict):
    """
    An ordered dictionary (:class:`collections.OrderedDict`) that returns a default value if a key does not exist and
    prints a warning.
    """
    # TODO should this dictionary be ordered alphabetically?

    defaults = {}

    # all aliases should be lower case
    aliases = {'DiffCoeff': ['d'],
               'Stiffness': ['k'],
               'CornerFreq': ['fc'],
               'PsdFitR2': ['r2'],
               'PsdFitChi2': ['chi2']}

    warningString = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return pprint.pformat(self)

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            try:
                value = self.defaults[item]
                log.info('%sDefault metadata value used for key: %s', self.warningString, item)
                return value
            except KeyError:
                pass
            raise

    def replace_key(self, oldKey, newKey):
        """
        Replace a key in the dictionary but keep its value. Since this is an ordered dictionary, the new key is added
        at the end.

        Args:
            oldKey (str): old key name
            newKey (str): new key name
        """

        if oldKey in self:
            self[newKey] = self.pop(oldKey)

    def get_alias(self, key):
        """
        Check if the given key corresponds to an alias in :attr:`tweezers.MetaBaseDict.aliases`.

        Args:
            key (str): string to check

        Returns:
            :class:`str`
        """

        for name, aliasList in self.aliases.items():
            if key.lower() == name.lower() or key.lower() in aliasList:
                return name
        return key

    def get_key(self, *keyElement):
        """
        Construct a key name for this dictionary from the input.
        If the input is a string, it is checked whether it exists or has an valid alias in the
        :attr:`tweezers.MetaBaseDict.aliases` attribute.
        If the input is a list of strings the elements are basically concatenated with the exception of the first
        element being of type ``pmx``. In this case e.g. ``['pmx', 'Stiffness']`` becomes ``pmStiffnessX``. Each of
        the list elements is checked for an valid alias with :meth:`tweezers.MetaBaseDict.get_alias`.

        Args:
            keyElement (:class:`str` or :class:`list` of :class:`str`): element(s) that describe the key to construct

        Returns:
            :class:`str`
        """

        # keyElement is a list
        # check if the list begins with something like 'pmx'
        regex = re.compile('^(?P<beam>pm|aod)?\s?(?P<axes>x|y)?\s?(?P<source>source)?.*', re.IGNORECASE)
        res = regex.search(keyElement[0])
        prefixElements = []
        if res:
            if res.group('beam'):
                prefixElements.append(res.group('beam').lower())
            if res.group('axes'):
                prefixElements.append(res.group('axes').upper())
            if res.group('source'):
                prefixElements.append('Source')
        else:
            prefixElements.append(self.get_alias(keyElement[0]))

        # add all other elements
        suffix = ''
        for i in range(1, len(keyElement)):
            suffix += self.get_alias(keyElement[i])

        # lets check for existing keys
        # if one is found, return it; this actually returns the first matching key but that should be fine
        prefix = ''
        for pre in prefixElements:
            prefix += pre
            key = prefix + suffix
            if key in self:
                break

        # here, we don't care if the key actually exists so just return it, it could be a new one
        return key
    
    def get(self, *k):
        """
        The input is forwarded to :meth:`tweezers.MetaBaseDict.get_key` which gives a key. This method
        returns the corresponding value in the dictionary if it exists.
        
        Args:
            *k (str): any number of strings
           
        Returns:
            :class:`str`
        """

        k = self.get_key(*k)
        return self[k]

    def set(self, *k):
        """
        Set a value for the key that is returned by :meth:`tweezers.MetaBaseDict.get_key`. The last
        parameter is the value to be set.

        Args:
            *k (str): any number of strings followed by a value to store in the dictionary
        """

        value = k[-1]
        k = self.get_key(*k[:-1])
        self[k] = value

    def get_facets(self):
        """


        Args:


        Returns:

        """

        facets = {'pmX': {}, 'pmY': {}, 'aodX': {}, 'aodY': {}}

        for key, value in self.items():
            regex = re.compile('^(?P<beam>pm|aod)(?P<axes>x|y)(?P<element>.*)$', re.IGNORECASE)
            res = regex.search(key)
            if not res:
                continue
            axes = res.group('beam').lower() + res.group('axes').upper()
            facets[axes]['title'] = self['title']
            facets[axes]['axes'] = axes
            facets[axes][res.group('element')] = value

        return list(facets.values())


class MetaDict(MetaBaseDict):
    """
    An class to hold metadata.
    """
    # TODO order keys by alphabet

    defaults = {'title': 'no title'}

    warningString = 'Meta values: '


class UnitDict(MetaBaseDict):
    """
    Store units corresponding to metadata.
    """
    defaults = {'viscosity': 'pN s / nm^2',
                'pmXDiff': 'V',
                'pmYDiff': 'V',
                'aodXDiff': 'V',
                'aodYDiff': 'V'
    }

    warningString = 'Units: '


class TweezerData():
    """
    TweezerData structure for tweezers experiment data and metadata. It requires a data source object that provides certain
    methods That populate the properties of this class. Note that not all of these methods must be implemented,
    depending of your usage of the class. However, if your data source does not implement a certain method, the code
    will fail only when the according property is called since all of them are evaluated lazily.

    Currently supported properties that require a specific method in the data source:

        ============ ================================== ===================================
        property     required method in data source     data type
        ============ ================================== ===================================
        meta         get_metadata                       :class:`tweezers.MetaDict`
        units        get_metadata                       :class:`tweezers.UnitDict`
        data         get_data                           :class:`pandas.DataFrame`
        psdSource    get_psd                            :class:`pandas.DataFrame`
        ts           get_ts                             :class:`pandas.DataFrame`
        ============ ================================== ===================================

    The properties require standardized keys for some fields. Additional fields can be present but the ones listed
    here must have the specified names.

        =============== =============================================================================================
        property        standardized keys
        =============== =============================================================================================
        meta / units    TODO
        data            ``PMxdiff``, ``PMydiff``, ``AODxdiff``, ``AODydiff``
        psdSource / psd ``f``, ``PMx``, ``PMy``, ``AODx``, ``AODy``, ``fitPMx``, ``fitPMy``, ``fitAODx``, ``fitAODy``
        ts              ``PMxdiff``, ``PMydiff``, ``AODxdiff``, ``AODydiff``
        =============== =============================================================================================
    """

    def __init__(self, dataSource, verbose=True):
        """
        Constructor for Data

        Args:
            dataSource: a data source object like e.g. :class:`tweezers.io.source.TxtSourceMpi`
        """

        # store dataSource object
        self.dataSource = dataSource

        logger = log.getLogger()
        # logger.
        if verbose:
            logger.setLevel(log.INFO)
        else:
            logger.setLevel(log.WARNING)
        # log.basicConfig(format='%(levelname)s:%(message)s', level=level)

    @lazy
    def meta(self):
        """
        Attribute that holds the metadata of the experiment. It is evaluated lazily thus the metadata is read only
        when required.

        Returns:
            :class:`tweezers.MetaDict`
        """

        meta, units = self.dataSource.get_metadata()
        self.units = units
        return meta

    @lazy
    def units(self):
        """
        Attribute that holds the units to the corresponding meta data. This should be returned by the data source's
        ``get_metadata`` method as well. Evaluated lazily.

        Returns:
            :class:`tweezers.UnitDict`
        """

        meta, units = self.dataSource.get_metadata()
        self.meta = meta
        return units


    @lazy
    def data(self):
        """
        Attribute that holds the experiment data. It is evaluated lazily thus the data is read only when required.

        Returns:
            :class:`pandas.DataFrame`
        """

        return self.dataSource.get_data()

    @lazy
    def ts(self):
        """
        Attribute to hold the time series used for the thermal calibration. Evaluated lazily.

        Returns:
            :class:`pandas.DataFrame`
        """

        return self.dataSource.get_ts()

    @lazy
    def psdSource(self):
        """
        Attribute to hold the power spectrum of the thermal calibration of the experiment as read from the DataSource.
        Also evaluated lazily.

        Returns:
            :class:`pandas.DataFrame`
        """

        return self.dataSource.get_psd()

    @lazy
    def psdFitSource(self):
        """
        Attribute to hold the fit of the Lorentzian to the power spectrum of the thermal calibration of the
        experiment as read from the DataSource. Also evaluated lazily.

        Returns:
            :class:`pandas.DataFrame`
        """

        return self.dataSource.get_psd_fit()

    def psd(self):
        """
        Attribute to hold the power spectrum density. If called before :meth:`tweezers.Data.compute_psd`, an exception is
        raised.
        """

        raise ValueError('PSD not yet computed. Please call "compute_psd"-method first.')

    def psdFit(self):
        """
        Attribute to hold the Lorentzian fit to the power spectrum density. If called before
        :meth:`tweezers.Data.fit_psd`, an exception is raised.
        """

        raise ValueError('PSD fit not yet computed. Please call "fit_psd"-method first.')

    def compute_psd(self, **kwargs):
        """
        Compute the power spectrum density from the experiments time series which is stored in the ``psd`` attribute.
        All Arguments are forwarded to :class:`tweezers.psd.PsdComputation`.

        Returns:
            :class:`tweezers.TweezerData`
        """

        psdObj = PsdComputation(self, **kwargs)
        setattr(self, 'psd', psdObj.psd())
        return self

    def fit_psd(self, **kwargs):
        """
        Fits the PSD. All input is forwarded to the :class:`tweezers.analysis.psd.PsdFit` object.

        Returns:
            :class:`tweezers.TweezerData`
        """

        psdFitObj = PsdFit(self, **kwargs)
        setattr(self, 'psdFit', psdFitObj.fit())
        return self

    def thermal_calibration(self):
        """
        Perform a thermal calibration. Requires :meth:`tweezers.TweezerData.psd` and :meth:`tweezers.TweezerData.psdFit`

        Args:
            self

        Returns:
            :class:`tweezers.TweezerData`
        """

        return self
