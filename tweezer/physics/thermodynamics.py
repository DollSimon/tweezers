from tweezer.constants import Constant
from tweezer.constants import kB


def thermal_energy(temperature=298, units='pN nm'):
    """
    Thermal energy in units of [pN nm]

    Parameters
    ----------
    temperature : float
        Temperature in units of [K]
        Default: 298 K

    units : str
        Unit of the returned energy value
        Choices: 'pN nm', 'J', None
        Default: 'pN nm'

    Returns
    -------
    energy : float
        Thermal energy in [units] (default is [pN nm])
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

