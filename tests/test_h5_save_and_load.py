#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os, shutil

import sure
import unittest
import nose

import pandas as pd

from clint.textui import colored, puts, indent

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
    from tweezer.ixo.pandas_ import (h5_save, h5_load, rdata_save)
except ImportError, err:
    puts('')
    with indent(2):
        puts(colored.red('The tweezer package has not been correctly installed or updated.')) 
        puts('')
        puts('The following import error occurred: {}'.format(colored.red(err))) 
        puts('')


class TestPandasDataFrameIO:

    def setUp(self):
        self.current_dir = os.getcwd()
        os.mkdir("testDir")
        os.chdir("testDir")

        # create data
        self.data = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y': [5, 4, 3, 2, 1]})
        self.data.units = {'x': 'm', 'y': 'pN'}

        self.pure_data = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y': [5, 4, 3, 2, 1]})

        self.file = os.path.join(os.getcwd(), 'pandas_export.h5')
        self.file_b = os.path.join(os.getcwd(), 'pandas_export_b.h5')
        self.r_file = os.path.join(os.getcwd(), 'pandas_export.RData')


    def tearDown(self):
        os.chdir(self.current_dir)
        shutil.rmtree("testDir")

    def test_data_integrity(self):
        self.data.x[1].should.equal(2) 
        self.data.should.have.property("units")
        self.data.units['x'].should.be('m')

    def test_h5_saving_produces_files(self):
        h5_save(data_frame = self.data, h5_file = self.file)
        files = os.listdir(os.getcwd()) 
        ('pandas_export.h5').should.be.within(files)
        ('pandas_export.json').should.be.within(files)

    def test_h5_saving_handles_names_correctly(self):
        h5_save(data_frame = self.data, h5_file = self.file_b)
        files = os.listdir(os.getcwd()) 
        ('pandas_export_b.h5').should.be.within(files)
        ('pandas_export_b.json').should.be.within(files)

    def test_no_json_file_produced_if_dataframe_has_no_attributes(self):
        h5_save(data_frame = self.pure_data, h5_file = self.file)
        files = os.listdir(os.getcwd()) 
        ('pandas_export.h5').should.be.within(files)
        ('pandas_export.json').shouldnot.be.within(files)
        
    def test_json_file_contains_attribute_data(self):
        h5_save(data_frame = self.data, h5_file = self.file)

        # Read data
        with open('pandas_export.json') as f:
            json_data = json.load(f)

        json_data['units']['x'].should.equal('m') 
        
    def test_h5_saving_loading_round_trip(self):
        h5_save(data_frame = self.data, h5_file = self.file)
        data = h5_load(h5_file = 'pandas_export.h5')
        data.x[1].should.equal(2) 
        data.units['x'].should.be('m')
        
    def test_rdata_saving(self):
        rdata_save(data_frame = self.data, rdata_file = self.r_file)
        files = os.listdir(os.getcwd()) 
        ('pandas_export.RData').should.be.within(files)

        # read contents of RData file
        rd = r.load(file='pandas_export.RData')
        str(rd.rx(1)).should.equal('[1] "attributes"\n') 
        str(rd.rx(2)).should.equal('[1] "data"\n') 
        str(rd.rx(3)).should.equal('[1] "keys"\n') 
        str(rd.rx(4)).should.equal('[1] "units_x"\n') 
        str(rd.rx(5)).should.equal('[1] "units_y"\n') 
        



        


        
        






