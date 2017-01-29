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

    def filter(self, filterStr):
        """
        Filter keys based on whether they contain a substring or not.

        Args:
            filterStr (`str`): substring to filter keys for

        Returns:
            :class:`.TweezersCollection`
        """
        # string based filter for keys
        res = self.__class__()
        for key in self.keys():
            if filterStr in key:
                res[key] = self[key]

        return res

