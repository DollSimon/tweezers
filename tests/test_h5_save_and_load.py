#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sure
import unittest
import nose

import os, shutil

import pandas as pd

from tweezer.ixo.pandas_ import h5_save, h5_load

try:
    import simplejson as json
except:
    import json


class TestPandasDataFrameSaving:

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
        
        


        
        






