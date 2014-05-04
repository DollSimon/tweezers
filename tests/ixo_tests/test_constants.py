from tweezer.constants import kB, NA, h


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
