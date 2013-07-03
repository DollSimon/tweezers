#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os

import pandas as pd

try:
    import simplejson as json
except:
    import json


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



def main():
    data = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y': [5, 4, 3, 2, 1]})
    data.units = {'x': 'm', 'y': 'pN'}
    h5file = os.path.join(os.getcwd(), 'pandas_export.h5')
    current_dir = os.getcwd()
    print(current_dir)
    os.mkdir("testDir")
    os.chdir("testDir")
    h5_save(data, h5file)


if __name__ == '__main__':
    import tempfile
    import shutil
    TEMPDIR = tempfile.mkdtemp()
    try:
        main()
    finally:
        shutil.rmtree(TEMPDIR)

