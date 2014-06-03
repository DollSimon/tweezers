#!/usr/bin/env python
# coding=utf-8

import numpy as np

from tweezer.math.geometry import Point, Vector


def test_vector_instantiation():
    v1 = Vector(Point(2, 3, 4), Point(1, 2, 8))

    assert v1.start == Point(2, 3, 4)
    assert v1.end == Point(1, 2, 8)


def test_vector_length_and_direction():
    v1 = Vector()
    v2 = Vector(end=Point(2, 2, 2))
    v3 = Vector(start=Point(1, 1, 1), end=Point(3, 3, 3))

    assert v1.length == np.sqrt(3)
    assert v2.length == np.sqrt(12)
    assert v3.length == np.sqrt(12)


def test_vector_norm():
    v1 = Vector(end=Point(1, 2, 3))

    assert v1.norm() == np.sqrt(14)
    assert v1.norm(order=1) == 6.0
    assert v1.norm(order=np.inf) == 3.0
