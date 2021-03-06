from collections import OrderedDict
import pprint
import copy


class AttrDictMixin(object):
    """
    Mixin to allow dictionary element access via attribute notation, e.g.::

        dict['key'] = 'hello world'
        print(dict.key)

    It also implements the `__dir__` method to allow autocompletion for attributes and keys in Jupyter notebooks.
    """

    def __getattribute__(self, name):
        # we have to use __getattribute__ instead of __getattr__ here since the latter relies on __dir__ which is
        # reimplemented below
        try:
            return super().__getattribute__(name)
        except AttributeError:
            pass
        if name in self.keys():
            return self[name]
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    def __setattr__(self, name, value):
        # calling super-method here since we reimplemented __dir__ below
        if name in super().__dir__():
            return super().__setattr__(name, value)
        else:
            self[name] = value

    def __delattr__(self, name):
        if name in super().__dir__():
            return super().__delattr__(name)
        elif name in self.keys():
            del self[name]
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name))

    def __dir__(self):
        return super().__dir__() + list(self.keys())


class IndexedOrderedDict(AttrDictMixin, OrderedDict):
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

    def _repr_pretty_(self, p, cycle):
        name = self.__class__.__name__
        if cycle:
            p.text(name + '(...)')
        else:
            with p.group(len(name) + 2, name + '([', '])'):
                for idx, (key, value) in enumerate(self.items()):
                    if idx:
                        p.text(',')
                        p.breakable()
                    if isinstance(value, dict):
                        p.text("'{}': ".format(key))
                        p.pretty(value)
                    else:
                        p.pretty(key)

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

    def copy(self):
        """
        Returns a deep copy of the object

        Returns:
            same type as object
        """

        return copy.deepcopy(self)

    def addField(self, name):
        """
        Adds a key with the given name and creates a :class:`tweezers.ixo.collections.IndexedOrderedDict` as value.

        Args:
            name (str): name for the new field

        Returns:
            :class:`tweezers.ixo.collections.IndexedOrderedDict`
        """

        # don't overwrite existing keys
        if name in self.keys():
            return self

        self[name] = IndexedOrderedDict()
        return self


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


def dictStructure(dictionary, indent=4, level=0):
    """
    Get the structure of a dictionary. Returns an ``OrderedDict`` with the same keys
    as the one passed as input but the values replaced with its type.

    Args:
        dictionary (`dict`): dictionary to traverse
        indent (`int`): number of spaces to indent a level
        level (`int`): current level of indentation

    Returns:
        `str`
    """

    if not isinstance(dictionary, dict):
        raise AttributeError('dictStructure: No dict given')

    indentString = ' ' * indent * level
    content = ''
    for key, item in dictionary.items():
        if isinstance(item, dict):
            content += '{}{}:\n'.format(indentString, key)
            content += dictStructure(item, indent=indent, level=level+1)
        else:
            content += '{}{}: {}\n'.format(indentString, key, type(item))

    return content
