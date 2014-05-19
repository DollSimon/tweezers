#!/usr/bin/env python
#-*- coding: utf-8 -*-
import pytest

from numpy.testing import assert_almost_equal as aae

from tweezer.physics.viscosity import dynamic_viscosity_of_mixture


@pytest.mark.algorithm
def test_viscosity_calculation():
    aae(dynamic_viscosity_of_mixture(3, 3, 25), 0.0068792)
    aae(dynamic_viscosity_of_mixture(3, 0, 25), 0.00089274)
    aae(dynamic_viscosity_of_mixture(0, 3, 25), 0.90568)
    aae(dynamic_viscosity_of_mixture(4, 3, 5), 0.010586, 6)
