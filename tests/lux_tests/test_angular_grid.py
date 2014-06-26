# coding=utf-8

import pytest


def test_angular_grid_with_known_parameter():

    grid = angular_grid(2, 2)

    assert grid == numpy.array([0.7854,  2.3562, 0.7854, 2.3562])
