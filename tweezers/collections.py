import re

from tweezers.ixo.collections import IndexedOrderedDict


class TweezersCollection(IndexedOrderedDict):
    """
    Collection of :class:`.TweezersData`. Inherits from
    :class:`.IndexedOrderedDict` with keys being ID names.
    """

    def flatten(self):
        """
        Flatten a data collection, i.e. remove nested collections.

        Returns:
            :class:`.TweezersCollection`
        """

        keys = list(self.keys())

        for key in keys:
            if isinstance(self[key], TweezersCollection):
                self.update(self[key].flatten())
                self.pop(key)

        return self.sorted()

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
            if re.match(filterExp, key):
                res[key] = self[key]

        return res

