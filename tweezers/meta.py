from collections import OrderedDict, Mapping
import pprint
import re
import pandas as pd
import logging as log


class MetaBaseDict(OrderedDict):
    """
    An ordered dictionary (:class:`collections.OrderedDict`) that returns a default value if a key does not exist and
    prints a warning.
    The convention for key style is "camelCase" (start lower case, new words begin upper case).
    Please check the `knownKeyTypes` dictionary for keys, that are used by some methods of
    :class:`tweezers.TweezersData`. If you don't call these methods, you don't need these keys. Even then,
    if you import data, try to use these standard keys as much as possible and please extend the list when your
    modifications of the code rely on a key's existence.
    """
    # TODO should this dictionary be ordered alphabetically?

    defaults = {}

    warningString = ''

    knownKeyTypes = OrderedDict([
        # general stuff
        ('title', str),
        ('date', str),
        ('time', str),
        ('samplingRate', int),

        ('psdSamplingRate', int),
        ('psdNBlocks', lambda x: int(float(x))),
        ('psdBlockLength', int),
        ('psdOverlap', int),
        ('psdSamplingRate', int),

        # experiment conditions
        ('viscosity', float),

        # axis variables
        ('cornerFrequency', float),
        ('stiffness', float),
        ('displacementSensitivity', float),
        ('forceSensitivity', float),
        ('beadDiameter', float),

        # mostly for units
        ('timeseries', 'timeseries'),
        ('psd', 'psd'),
    ])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, value in self.items():
            if isinstance(value, Mapping):
                self[key] = self.__class__(value)

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

    def print(self):
        """
        Pretty print the meta dictionary.
        """

        pprint.pprint(self)

    def replaceKey(self, oldKey, newKey):
        """
        Replace a key in the dictionary but keep its value. Since this is an ordered dictionary, the new key is added
        at the end.

        Args:
            oldKey (str): old key name
            newKey (str): new key name
        """

        if oldKey in self:
            self[newKey] = self.pop(oldKey)

    def deleteKey(self, *args):
        """
        Delete one or multiple keys from the dictionary.

        Args:
            key (str): one or mulitple keys to (recursively) delete from the dictionary
        """

        keys = args

        # loop through dict and check for element
        for key, value in self.items():
            if isinstance(value, MetaBaseDict):
                value.deleteKey(*keys)
            else:
                if key in keys:
                    self.pop(key)


    def getFacets(self):
        """
        Create a :class:`pandas.DataFrame` facet view of the metadata. Useful for facet plotting using
        :class:`seaborn.FacetGrid`.

        Args:
            beams (list): list of strings describing the available beams (e.g. `['pm', 'aod']`)
            axes (list): list of strings describing the available measured axes per beam (e.g. `['x', 'y']`)

        Returns:
            :class:`pandas.DataFrame`
        """

        facets = {}

        # each axis will be a row in the final dataframe so each of them needs to have all the metadata
        generalMeta = {}
        for key, value in self.items():
            if isinstance(value, self.__class__):
                facets[key] = value
                facets[key]['axis'] = key
            else:
                generalMeta[key] = value

        for key, value in facets.items():
            value.update(generalMeta)

        # convert to pandas DataFrame
        facets = pd.DataFrame(list(facets.values()))

        return facets

    def update(self, E=None, **F):
        # we assume E to be a dictionary type (have a .keys() method), F is one anyway
        todo = [E, F]
        # loop through the two dicts
        for el in todo:
            # if an element was given...
            if el:
                # ...go through all its items...
                for key, value in el.items():
                    # ... and check if they are a Mapping type
                    if isinstance(value, Mapping):
                        # if so, start recursion
                        if key in self:
                            self[key].update(value)
                        else:
                            self[key] = self.__class__(value)
                    else:
                        # else, just update
                        self[key] = value

    def subDictKeys(self):
        """
        Returns the keys of elements which are :class:`tweezers.meta.MetaBaseDict` or inherited from it.

        Returns:
            list of strings
        """

        keys = [key for key, value in self.items() if isinstance(value, MetaBaseDict)]
        return keys

class MetaDict(MetaBaseDict):
    """
    An class to hold metadata.
    """
    # TODO order keys by alphabet

    defaults = {'title': 'no title',
                'temperature': 25,
                'psdSamplingRate': 80000
    }

    warningString = 'Meta values: '


class UnitDict(MetaBaseDict):
    """
    Store units corresponding to metadata.
    """
    defaults = {'viscosity': 'pN s / nm^2',
                'pmXDiff': 'V',
                'pmYDiff': 'V',
                'aodXDiff': 'V',
                'aodYDiff': 'V',
                'temperature': '˚C',
                'psdSamplingRate': 'Hz',
                'psd': 'V²/Hz'
    }

    warningString = 'Units: '
