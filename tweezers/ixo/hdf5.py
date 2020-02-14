import numpy as np
import pandas as pd
from collections import OrderedDict
import hdf5storage
from datetime import datetime

from tweezers.meta import MetaDict, UnitDict
from tweezers.ixo.collections import IndexedOrderedDict


class CustomNumpyMarshaller(hdf5storage.Marshallers.NumpyScalarArrayMarshaller):
    def __init__(self):
        super().__init__()

    def read(self, f, dsetgrp, attributes, options):
        data = super().read(f, dsetgrp, attributes, options)
        # remove dimensions of size 1
        data = data.squeeze()
        # if the array contains 1 element, return it instead of the array
        if not data.shape:
            data = data[()]
        return data


class TimestampMarshaller(hdf5storage.Marshallers.PythonStringMarshaller):
    types = [datetime,
             'pandas._libs.tslibs.timestamps.Timestamp']

    def __init__(self):
        super().__init__()

        self.types = [datetime,
                      'pandas._libs.tslibs.timestamps.Timestamp']
        self.python_type_strings = ['datetime.datetime',
                                    'pandas._libs.tslibs.timestamps.Timestamp']
        self.matlab_classes = []
        self.update_type_lookups()

    def read(self, f, dsetgrp, attributes, options):
        # read string
        timeStr = super().read(f, dsetgrp, attributes, options)
        # convert to timestamp
        time = datetime.fromisoformat(timeStr)
        return time

    def write(self, f, grp, name, data, type_string, options):
        # convert timestamp to string
        timeStr = data.isoformat()
        # write data
        super().write(f, grp, name, timeStr, 'datetime.datetime', options)


class IndexedOrderedDictMarshaller(hdf5storage.Marshallers.PythonDictMarshaller):
    def __init__(self):
        super().__init__()

        # append Python types to use this marshaller for
        self.types += [MetaDict,
                       UnitDict,
                       IndexedOrderedDict]
        self.python_type_strings += ['tweezers.MetaDict',
                                     'tweezers.UnitDict',
                                     'tweezers.ixo.collections.IndexedOrderedDict']
        # add tranlsation from Python to Matlab types
        self.__MATLAB_classes = {dict: 'struct',
                                 OrderedDict: 'struct',
                                 MetaDict: 'struct',
                                 UnitDict: 'struct',
                                 IndexedOrderedDict: 'struct'}
        # set default conversion for Matlab to Python
        self.__MATLAB_classes_reverse = {'struct': IndexedOrderedDict}
        self.matlab_classes.append('struct')

        self.update_type_lookups()
        # use this marshaller if no type information can be inferred, library defaults to strutured numpy array
        self.typestring_to_type[None] = IndexedOrderedDict


class DataFrameMarshaller(IndexedOrderedDictMarshaller):
    def __init__(self):
        super().__init__()

        self.types = [pd.DataFrame]
        self.python_type_strings = ['pandas.DataFrame']
        self.matlab_classes = ['struct']

    def write(self, f, grp, name, data, type_string, options):
        # check input
        if isinstance(data.index, pd.MultiIndex):
            raise ValueError('Saving MultiIndex DataFrames is not supported.')
        if not data.columns.is_unique:
            raise ValueError("DataFrame columns are not unique, some columns will be omitted.")

        # convert dataframe to ordereddict
        data = OrderedDict((k, v.values) for k, v in data.iteritems())
        # store using existing routines
        super().write(f, grp, name, data, 'pandas.DataFrame', options)
        return

    def read(self, f, dsetgrp, attributes, options):
        typeSafe = False
        if attributes['Python.Type']:
            # we came here from the proper Python type and can convert directly to a DataFrame
            typeSafe = True

        # adjust type for proper handling of data by parent class
        attributes['Python.Type'] = 'tweezers.ixo.collections.IndexedOrderedDict'
        # read data
        data = super().read(f, dsetgrp, attributes, options)

        if typeSafe:
            # convert to DataFrame
            data = pd.DataFrame(data)
        else:
            # we came here from a Matlab struct, have to check data content
            # all all dict fields arrays with numeric content?
            allNumArray = True
            for v in data.values():
                # check for:
                #   - array type
                #   - if array is numeric, unfortunately the array type is 'O' so we check the first element
                try:
                    if type(v) is not np.ndarray \
                            or not np.issubdtype(type(v[0]), np.number):
                        allNumArray = False
                except:
                    allNumArray = False

            if allNumArray:
                # attempt conversion
                try:
                    data = pd.DataFrame(data)
                except ValueError:
                    pass
        return data


class CustomMarshallerCollection(hdf5storage.MarshallerCollection):
    def __init__(self, **kwargs):
        kwargs['marshallers'] = [DataFrameMarshaller(), IndexedOrderedDictMarshaller(), CustomNumpyMarshaller(),
                                 TimestampMarshaller()]
        kwargs['priority'] = ('user', 'builtin', 'plugin')
        super().__init__(**kwargs)


def save(path, data):
    """
    Save data in a Matlab compatible format.

    Args:
        path (str or pathlike): path to the file to save
        data: data to save
    """

    collect = CustomMarshallerCollection()
    hdf5storage.savemat(str(path), data,
                        marshaller_collection=collect,
                        truncate_existing=True,
                        format='7.3',
                        appendmat=False)


def load(path, keys=None):
    """
    Load data from a Matlab compatible file.

    Args:
        path (str or pathlike): path to the file to read
        keys: optional, read only some keys from the file

    Returns:
        data
    """

    collect = CustomMarshallerCollection()
    return hdf5storage.loadmat(str(path), marshaller_collection=collect,
                               appendmat=False, variable_names=keys)
