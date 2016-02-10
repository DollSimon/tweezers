"""
General scientific constants
"""


class Constant(float):

    def __new__(cls, value, unit):
        return float.__new__(cls, value)

    def __init__(self, value, unit=None):
        self.unit = unit

kB = Constant(1.3806488e-23, 'J/K')
kB.__doc__ = """\
Boltzmann constant [J/K]
"""

h = Constant(6.62606957e-34, 'J * s')
h.__doc__ = """\
Planck's constant [J * s]
"""

NA = Constant(6.02214129e23, '1/mol')
NA.__doc__ = """\
Avogadro's constant [1 / mol]
"""

vacuumPermittivity = Constant(8.854187817620e-12, 'F/m')
vacuumPermittivity.__doc__ = """\
Permittivity in free space.
"""

c = Constant(299792458, 'm/s')
c.__doc__ = """\
Speed of light
"""
