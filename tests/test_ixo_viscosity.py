#!/usr/bin/env python
#-*- coding: utf-8 -*-
import pytest

from tweezer.ixo.viscosity import dynamic_viscosity_of_mixture


@pytest.mark.wip
# @pytest.mark.parametrize("W, G, T, expected", [
#     ("0.4", "2.3", "25", 0.11667),
#     ("3", "3", "25", 0.0068792),
#     ("0", "3", "25", 0.90568),
#     ("4", "3", "5", 0.010586),
#     ("3", "0", "25", 0.00089274)])
# def test_viscosity_of_known_solutions(W, G, T, expected):
#     assert dynamic_viscosity_of_mixture(W, G, T) == expected
def test_viscosity_calculation():
    # assert dynamic_viscosity_of_mixture(3, 3, 25) == 0.0068792
    # assert dynamic_viscosity_of_mixture(3, 0, 25) == 0.00089274
    assert dynamic_viscosity_of_mixture(0, 3, 25) == 0.90568
    assert dynamic_viscosity_of_mixture(4, 3, 5) == 0.010586
