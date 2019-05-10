from scipy import constants as const


def kbt(temperature=25):
    """
    Thermal energy in units of [pN nm]

    Args:
        temperature (`float`): temperature in units of [C]. (optional, default 25)

    Returns:
        `float` -- thermal energy in [pN nm]
    """

    return const.k * (temperature + 273.15) * 1E21
