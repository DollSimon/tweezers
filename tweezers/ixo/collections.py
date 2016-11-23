from collections import OrderedDict


class AttrDictMixin(object):
    # todo docstring
    def __getattr__(self, item):
        if item in self.__dir__():
            return getattr(self, item)
        elif item in self.keys():
            return self[item]
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, item))

    def __setattr__(self, name, value):
        if name in self.__dir__():
            return setattr(self, name, value)
        else:
            self[name] = value

    def __delattr__(self, item):
        if item in self.__dir__():
            return delattr(self, item)
        elif item in self.keys():
            del self[item]
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, item))


class IndexedOrderedDict(OrderedDict, AttrDictMixin):
    #ToDo: docstring

    def __getitem__(self, item):
        if isinstance(item, int):
            # numeric indexing
            key = list(self.keys())[item]
            return self[key]
        if isinstance(item, slice):
            if isinstance(item.start, str):
                # slicing with string as 'start'
                try:
                    start = self.index(item.start)
                except ValueError:
                    # 'from None' suppresses the 'ValueError' and only raises the KeyError
                    raise KeyError("'{}'".format(item.start)) from None
            else:
                start = item.start
            if isinstance(item.stop, str):
                try:
                    stop = self.index(item.stop)
                except ValueError:
                    raise KeyError("'{}'".format(item.stop)) from None
            else:
                stop = item.stop
            sl = slice(start, stop, item.step)
            # return slice
            keys = list(self.keys())[sl]
            values = list(self.values())[sl]
            return self.__class__(zip(keys, values))
        else:
            # classical key based indexing
            return super().__getitem__(item)

    def index(self, key):
        # todo docstring
        return list(self.keys()).index(key)

    def key(self, index):
        # todo docstring
        if isinstance(index, int):
            # numeric indexing
            return list(self.keys())[index]
        else:
            # traditional indexing
            return index

    def sorted(self, key=lambda t: t[0]):
        # todo docstring
        # by default orders by key
        return self.__class__(sorted(self.items(), key=key))

    def pop(self, item, *args):
        if isinstance(item, int):
            # numeric indexing
            key = list(self.keys())[item]
        else:
            key = item
        return super().pop(key, *args)
