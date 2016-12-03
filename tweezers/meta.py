from collections import OrderedDict, Mapping
import pprint
import pandas as pd
import logging as log

from tweezers.ixo.collections import AttrDictMixin


class MetaBaseDict(OrderedDict, AttrDictMixin):
    """
    An ordered dictionary (:class:`collections.OrderedDict`) that returns a default value if a key does not exist and
    prints a warning.
    The convention for key style is "camelCase" (start lower case, new words begin upper case).

    Note that if you read data from a new data source, it is recommended to stick to the reference key naming in the
    meta data. The reference is the header of the Biotec txt files.
    """

    defaults = {}

    warningString = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, value in self.items():
            if isinstance(value, Mapping):
                self[key] = self.__class__(value)

    def __str__(self):
        #ToDo: consider switching to pprint++: https://github.com/wolever/pprintpp
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

        delKeys = args
        keys = self.keys()
        for key in delKeys:
            if key in keys:
                self.pop(key)

        for key in self.subDictKeys():
            self[key].deleteKey(*delKeys)

    def getFacets(self):
        """
        Create a :class:`pandas.DataFrame` facet view of the metadata. Useful for facet plotting using
        :class:`seaborn.FacetGrid`.

        Returns:
            :class:`pandas.DataFrame`
        """

        facets = []

        # each axis will be a row in the final dataframe so each of them needs to have all the metadata
        generalMeta = {}
        for key, value in self.items():
            if isinstance(value, self.__class__):
                facets.append(value.copy())
                facets[-1]['axis'] = key
            else:
                generalMeta[key] = value

        # remove not needed keys
        generalMeta.pop('traps', None)

        # turn into a DataFrame
        facets = pd.DataFrame(facets)
        # add general data to each row
        facets = facets.assign(**generalMeta)

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
                'psd': 'V²/Hz',
                'timeseries': 'V',
    }

    warningString = 'Units: '
