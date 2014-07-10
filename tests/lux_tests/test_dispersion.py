# coding=utf-8
from tweezer.physics.materials import SellmeierCoefficients
from tweezer.lux.dispersion import dispersion

SELLMEIER_COEFFICIENTS_BK7 = SellmeierCoefficients(1.03961212,
                                                   0.231792344,
                                                   1.01046945,
                                                   6.00069867E-3,
                                                   2.00179144E-2,
                                                   1.03560653E2)

def test_dispersion_with_BK7():
    n = dispersion(1.064, SELLMEIER_COEFFICIENTS_BK7)

    assert n == 1.5
