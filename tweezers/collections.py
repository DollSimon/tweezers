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

        for key, value in self.items():
            if isinstance(value, TweezersCollection):
                self.pop(key)
                value.flatten()
                self.update(value)

        return self.sorted()
