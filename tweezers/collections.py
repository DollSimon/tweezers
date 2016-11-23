from tweezers.ixo.collections import IndexedOrderedDict


class TweezersCollection(IndexedOrderedDict):
    # ToDo: Docstring
    pass

    @property
    def length(self):
        #todo docstring

        return len(self)
