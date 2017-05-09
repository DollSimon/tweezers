import re
import pandas as pd

from tweezers.ixo.collections import IndexedOrderedDict


class TweezersCollection(IndexedOrderedDict):
    """
    Collection of :class:`.TweezersData`. Inherits from
    :class:`.IndexedOrderedDict` with keys being ID names.
    """

    def flatten(self):
        """
        Flatten a data collection, i.e. remove nested collections. Returns a copy of the collection.

        Returns:
            :class:`.TweezersCollection`
        """

        res = self.__class__()
        keys = list(self.keys())

        for key in keys:
            if isinstance(self[key], TweezersCollection):
                # if the item is a collection itself, append its flattened result
                res.update(self[key].flatten())
            else:
                # append the item directly
                res[key] = self[key]

        return res.sorted()

    def filter(self, filterExp):
        """
        Filter keys based on whether they match a regular filter expression or not.

        Args:
            filterExp (`str`): regular expression to filter keys

        Returns:
            :class:`.TweezersCollection`

        Example:
            ::

                 path = '/Volumes/grill/Tweezers/Data/Raw/data'
                 ids = getAllIds(path)
                 fids = ids.filter('2017-03.*Hyd')
        """
        # string based filter for keys
        res = self.__class__()
        for key in self.keys():
            if re.search(filterExp, key):
                res[key] = self[key]

        return res

    def getMetaFacets(self):
        """
        Create a :class:`pandas.DataFrame` facet view of the metadata of all datasets. This calls
        :meth:`tweezers.meta.MetaBaseDict.getFacets`.

        Returns:
            :class:`pandas.DataFrame`
        """

        res = []
        for item in self.values():
            if isinstance(item, TweezersCollection):
                res.append(item.getMetaFacets())
            else:
                res.append(item.meta.getFacets())

        return pd.concat(res, ignore_index=True)
