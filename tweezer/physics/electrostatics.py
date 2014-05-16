from tweezer.constants import Constant
from tweezer.constants import kB, vacuumPermittivity


def bjerrum_length(temperature=298, units='pN nm'):
    """
    Separation at which the electrostatic interaction between two elementary charges is \
    comparable in magnitude to the thermal energy.

    Parameters
    ----------
    temperature : float
        Temperature in units of [K]
        Default: 298 K

    Returns
    -------
    length : float
        Bjerrum length
    """
    raise NotImplementedError()

