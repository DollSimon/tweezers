#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os

import pandas as pd

from clint.textui import puts, indent, colored

try:
    import simplejson as json
except:
    import json

try:
    from rpy2.robjects import r
    import pandas.rpy.common as com
except:
    raise ImportError('Probably the rpy2 library is not working...')

try:
    from tweezer.ixo.collections_ import flatten_dictionary
except ImportError as err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.'))
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err)))
        puts('')


def h5_save(data_frame=None, h5_file='test.h5', append_data=False):
    """
    Saves pandas DataFrame with additional attributes to h5 file format. Since custom attributes can't be stored like this yet, these are recognised and saved as json file format with the same name.

    Parameter:
    ----------

    :param data_frame:(pandas.DataFrame) that might carry additional custom attributes
    :param h5_file: (path) where to save the data
    :param append_data: (Boolean) whether the data should be appended to an existing file

    """
    if not h5_file.endswith('.h5'):
        raise IOError('Please specify an hdf5 file with extension .h5')

    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError('Provided data is not of type pandas.DataFrame, but {}'.format(type(data_frame)))

    # get attributes if any
    EMPTY_FRAME = pd.DataFrame()

    attributes = list(set(dir(EMPTY_FRAME)) ^ set(dir(data_frame)))

    if attributes:
        json_file = os.path.splitext(h5_file)[0] + '.json'

        json_dic = {}
        json_dic['attributes'] = attributes
        json_dic['keys'] = str(data_frame.keys())

        for attribute in attributes:
            json_dic[attribute] = data_frame.__getattribute__(attribute)
    else:
        json_file = None

    # write files
    if not os.path.exists(h5_file):
        try:
            store = pd.HDFStore(h5_file)
            store.put('data', data_frame)
            store.close()
        except:
            raise
    else:
        print('File already exists')

    if json_file:
        if not os.path.exists(json_file):
            with open(json_file, 'w') as f:
                json.dump(json_dic, f)
        else:
            print('File already exists')


def h5_load(h5_file):
    """
    Load pandas DataFrame from an h5 file. If there exists a .json file of the same name in the same directory the content of that file is parsed as custom attributes attached to the DataFrame

    :param h5_file: (path) of h5 file from which to load the data.

    :return data: (pandas.DataFrame) with saved attributes if they exist

    """
    if not h5_file.endswith('.h5'):
        raise IOError('Please specify an hdf5 file with extension .h5')

    # handling the data frame
    store = pd.HDFStore(h5_file)
    data = store.get('data')
    store.close()

    # handling eventual attributes
    json_file_name = ".".join([os.path.splitext(os.path.basename(h5_file))[0], 'json'])
    json_file = os.path.join(os.path.dirname(h5_file), json_file_name)

    if os.path.isfile(json_file):
        with open(json_file, 'r') as f:
            json_dic = json.load(f)

        try:
            attributes = json_dic['attributes']
            for attribute in attributes:
                data.__setattr__(attribute, json_dic[attribute])
        except:
            raise

    return data


def rdata_save(data_frame=None, rdata_file='test.RData', append_data=False):
    """
    Saves pandas DataFrame with additional attributes to RData file format. Since custom attributes can't be stored like this yet, these are recognised and saved as json file format with the same name.

    Parameter:
    ----------

    :param data_frame:(pandas.DataFrame) that might carry additional custom attributes
    :param rdata_file: (path) where to save the data
    :param append_data: (Boolean) whether the data should be appended to an existing file

    """
    if not rdata_file.endswith('.RData'):
        raise IOError('Please specify an RData file with extension .RData')

    if not isinstance(data_frame, pd.DataFrame):
        raise TypeError('Provided data is not of type pandas.DataFrame, but {}'.format(type(data_frame)))

    # get attributes if any
    EMPTY_FRAME = pd.DataFrame()

    attributes = list(set(dir(EMPTY_FRAME)) ^ set(dir(data_frame)))

    # write files
    if not os.path.exists(rdata_file):
        try:
            r_data_frame = com.convert_to_r_dataframe(data_frame)
            r.assign('data', r_data_frame)

            if attributes:

                r_dic = {}
                r_dic['attributes'] = attributes
                r_dic['keys'] = str(data_frame.keys())

                for attribute in attributes:
                    r_dic[attribute] = data_frame.__getattribute__(attribute)

                flatten = lambda d: {'_'.join(k):v for k,v in flatten_dictionary(d).items()}

                for key, value in flatten(r_dic).items():
                    try:
                        r.assign('{}'.format(key), value)
                    except:
                        print('Could not export {} to R...'.format(key))

            r("save.image(file = '{}')".format(rdata_file))

        except:
            raise
    else:
        print('File already exists')

