def asKelvin(temperatureInCelsius=25):
    """
    Converts temperature from Celsius to Kelvin

    Args:
        temperatureInCelsius (float): Temperature in [°C]. (Default: 25 °C)

    Returns:
        temperatureInKelvin (float): Temperature in Kelvin [K]
    """
    assert temperatureInCelsius >= -273.15

    temperatureInKelvin = 273.15 + temperatureInCelsius

    return temperatureInKelvin


def asCelsius(temperatureInKelvin=298):
    """
    Converts temperature from Kelvin to Celsius

    Args:
        temperatureInKelvin (float): Temperature in Kelvin [K]. (Default: 298 K)

    Returns:
        temperatureInCelsius (float): Temperature in [°C]. (Default: 25 °C)
    """
    assert temperatureInKelvin >= 0

    temperatureInCelsius = temperatureInKelvin - 273.15

    return temperatureInCelsius
