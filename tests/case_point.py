#!/usr/bin/env python
#-*- coding: utf-8 -*-

from tweezer.geom.point import Point

import sure

describe "a very simple test case for my_module":

    it "has a foo property that is False":
        assert my_module.foo == False

describe "a simple point":

    it "can be declared like Point(1, 2, 3)":
        p = Point(1, 2, 3)
        p.should.be.a('Point')
