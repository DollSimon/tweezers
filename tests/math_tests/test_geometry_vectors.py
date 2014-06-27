#!/usr/bin/env python
# coding=utf-8

import numpy as np
from numpy.testing import assert_almost_equal as aae


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


def test_common_operations_between_vectors():
    v1 = Vector(end=Point(1, 2, 3))
    v2 = Vector(end=Point(2, 2, 2))

    v3 = v2 - v1
    v4 = v2 + v1
    v5 = v1 + v2

    assert v3.coordinates == [1, 0, -1]
    assert v4.coordinates == [3, 4, 5]
    assert v5.coordinates == [3, 4, 5]


def test_negation_of_vectors():
    v1 = Vector(end=Point(1, 2, 3))
    v2 = -v1

    assert v2.end == v1.start
    assert v2.start == v1.end


def test_right_angle_between_vectors():
    v1 = Vector(end=Point(1, 0, 0))
    v2 = Vector(end=Point(0, 0, 1))

    angle = v1.angleTo(v2, inDegrees=True)

    assert angle == 90


def test_angle_between_vectors():
    v1 = Vector(end=Point(1, 2, 3))
    v2 = Vector(end=Point(4, 5, 6))

    angle = v1.angleTo(v2, inDegrees=True)

    aae(angle, 12.93315, decimal=4)
