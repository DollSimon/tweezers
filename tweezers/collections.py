from tweezers.ixo.collections import IndexedOrderedDict


class TweezersCollection(IndexedOrderedDict):
    # ToDo: Docstring

    @property
    def length(self):
        #todo docstring

        return len(self)

    def flatten(self):
        # todo docstring
        # flatten a data collection (remove nested collections)

        keys = list(self.keys())

        for key in keys:
            if isinstance(self[key], TweezersCollection):
                self.update(self[key].flatten())
                self.pop(key)

        return self.sorted()

    def filter(self, filterStr):
        # todo docstring
        # string based filter for keys
        res = self.__class__()
        for key in self.keys():
            if filterStr in key:
                res[key] = self[key]

        return res

