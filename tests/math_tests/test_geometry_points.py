#!/usr/bin/env python
# coding=utf-8

import numpy as np

from tweezer.math.geometry import Point


def test_simple_point_instantiation():
    p1 = Point(1, 2, 3)
    p2 = Point(3, 4.3)
    p3 = Point(y=4.3, z=-5.4)

    assert p1.x == 1
    assert p1.y == 2
    assert p1.z == 3

    assert p2.x == 3
    assert p2.y == 4.3
    assert p2.z == 0

    assert p3.x == 0
    assert p3.y == 4.3
    assert p3.z == -5.4

    assert p1.coordinates == [1, 2, 3]


def test_creating_points_from_list():
    p1 = Point([2, 3, 4])

    assert p1 == Point(2, 3, 4)


def test_equality_operation_for_points():
    p1 = Point(2, 3, 4)

    assert p1 == Point(2, 3, 4)
    assert p1 != Point(0, 0, 0)


def test_creating_point_at_origin():
    o = Point.origin()

    assert o.x == 0
    assert o.y == 0
    assert o.z == 0


def test_distance_to_origin():
    p1 = Point(2, 2, 2)

    assert p1.distanceToOrigin == np.sqrt(12)


def test_common_operations_between_points():
    p1 = Point(1.2, -2.2, 3)
    p2 = Point(4, 3, 2)
    p3 = Point(3, 2)

    assert p2 - p1 == Point(2.8, 5.2, -1)
    assert p3 * 3 == Point(9, 6, 0)
    assert p2 + p3 == Point(7, 5, 2)
    assert p3 / 10 == Point(0.3, 0.2)


def test_common_right_hand_side_operations():
    p1 = Point(1.2, -2.2, 3)
    p2 = Point(4, 3, 2)
    p3 = Point(3, 2)

    assert 3 * p3 == Point(9, 6, 0)
    assert 4 + p2 == Point(8, 7, 6)


def test_iteration_on_coordinates():
    p1 = Point(1, 2, 3)
    p2 = Point(2.3, -4.3)

    coordinates1 = [x for x in p1]
    coordinates2 = [x for x in p2]

    assert coordinates1 == [1, 2, 3]
    assert coordinates2 == [2.3, -4.3, 0]

