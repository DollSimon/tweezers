from tweezer.constants import Constant
from tweezer.constants import kB


def thermal_energy(temperature=298, units='pN nm'):
    """
    Thermal energy in units of [pN nm]

    :param temperature: Temperature in units of [K]
    :param units: change the units and value of the returned energy

    :return energy: Thermal energy in [pN nm] (default)
    """
    if units is None:
        energy = kB * temperature
    elif 'pN nm' in units:
        energy = Constant(kB * temperature * 10**(21))
        energy.unit = 'pN nm'
    elif 'J' in units:
        energy = Constant(kB * temperature)
        energy.unit = 'J'
    else:
        raise BaseException("Can't figure out how to return thermal energy value")

    return energy

