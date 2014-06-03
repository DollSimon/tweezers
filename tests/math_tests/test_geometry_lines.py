#!/usr/bin/env python
# coding=utf-8

import numpy as np

from tweezer.math.geometry import Point, Line


def test_line_instantiation_from_points():
    l1 = Line(Point(2, 3, 4), Point(1, 2, 8))
    p1 = Point(2, 3, 4)

    assert l1.direction == UnitVector(Point(2, 3, 4), Point(1, 2, 8))
    assert l1.anchor == Point(2, 3, 4)
    assert p1 in l1


def test_line_instantiation_from_vector():
    l1 = Line(Vector())

    assert l1.anchor == Point(0, 0, 0)
    assert l1.direction == [1/3, 1/3, 1/3]
