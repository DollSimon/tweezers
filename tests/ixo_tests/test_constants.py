from numpy.testing import assert_approx_equal

from tweezer.legacy.physics2.constants import kB, NA, h
from tweezer.physics import thermal_energy


def test_values_of_general_physical_constants():

    # Boltzmann
    assert kB == 1.3806488e-23
    assert kB.unit == 'J/K'

    # Planck
    assert h == 6.62606957e-34
    assert h.unit == 'J * s'

    # Avogadro
    assert NA == 6.02214129e23
    assert NA.unit == "1/mol"


def test_default_thermal_engergy_calculations():

    kBT = thermal_energy()

    assert_approx_equal(kBT, 4.114333424, significant=7)
    assert kBT.unit == 'pN nm'


def test_different_unit_in_thermal_energy_calculations():

    kBT = thermal_energy(units='J')

    assert kBT.unit == 'J'
    assert_approx_equal(kBT, 4.1143334e-21)


def test_thermal_energy_without_units():

    kBT = thermal_energy(units=None)

    assert_approx_equal(kBT, 4.1143334e-21)

