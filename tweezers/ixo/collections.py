from collections import OrderedDict, Iterable
import pprint


class AttrDictMixin(object):
    """
    Mixin to allow dictionary element access via attribute notation, e.g.::

        dict['key'] = 'hello world'
        print(dict.key)
    """

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
    """
    An ordered dictionary whose elements can be accessed
        * in the classic dict ``dict['key']``
        * using the attribute access method ``dict.key``
        * or via a numeric index ``dict[0]``

    Slicing works with keys and numeric indices.
    """

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
        """
        Get numeric index of given key.

        Args:
            key (`str`): key name

        Returns:
            `int`
        """

        return list(self.keys()).index(key)

    def key(self, index):
        """
        Get key name for given numeric index.

        Args:
            index (`int`): numeric index

        Returns:
            `str`
        """

        if isinstance(index, int):
            # numeric indexing
            return list(self.keys())[index]
        else:
            # traditional indexing
            return index

    def sorted(self, key=lambda t: t[0]):
        """
        Return sorted version of the dictionary.

        Args:
            key: see `sorted` documentation, defaults to sort bey dictionary key

        Returns:
            :class:`tweezers.ixo.collections.IndexedOrderedDict`
        """

        # by default orders by key
        return self.__class__(sorted(self.items(), key=key))

    def pop(self, item, *args):
        """
        Remove item from dictionary.

        Args:
            item (`int` or `str`): remove element identified by key or numeric index from dictionary
            *args: forwarded to :meth:`collections.OrderedDict.pop`

        Returns:
            the removed element
        """
        if isinstance(item, int):
            # numeric indexing
            key = list(self.keys())[item]
        else:
            key = item
        return super().pop(key, *args)

    def __str__(self):
        # pretty-print output of the dict
        return pprint.pformat(super().__str__())

    @property
    def length(self):
        """
        Get the number of elements in the dictionary.

        Returns:
            `int`
        """

        return len(self)


def isNestedDict(dictionary):
    """
    Checks if a dictionary contains subdictionaries.

    Args:
        dictionary (`dict`): dictionary to check

    Returns:
        `bool`
    """

    if not isinstance(dictionary, dict):
        raise ValueError('isNestedDict: No dict given')

    for key in dictionary.keys():
        if isinstance(dictionary[key], dict):
            return True

    return False
