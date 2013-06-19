#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pandas as pd


def h5_save(h5_file, DataFrame):
    """
    Saves pandas DataFrame with additional attributes to h5 file format. Since custom attributes can't be stored like this yet, these are recognised and saved as json file format with the same name.
    
    :param h5_file: (path) where to save the data
    :param DataFrame: (pandas.DataFrame) that might carry additional custom attributes
    """
    # get attributes if any
    REF = pd.DataFrame([])
     
    attributes = list(set(dir(REF)) ^ set(dir(data)))

    if attributes:
        pass


def h5_load(h5_file):
    """
    Load pandas DataFrame from an h5 file. If there exists a .json file of the same name in the same directory the content of that file is parsed as custom attributes attached to the DataFrame
    
    :param h5_file: (path) of h5 file from which to load the data.
    """
    jFile = os.path.join(os.path.dirname(h5_file), ".".join([os.path.splitext(os.path.basename(h5_file))[0], 'json']))

    if os.path.isfile(jFile):
        pass
