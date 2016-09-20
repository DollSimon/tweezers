from collections import OrderedDict
from tweezers.physics.tweezers import distanceCalibration, trapStiffness


def thermalCalibration(diffCoeff, cornerFreq, viscosity, beadDiameter, temperature=25):
    """
    Perform the thermal calibration for the given input parameters. This calculates the trap stiffness, displacement
    sensitivity and force sensitivity of the trap.

    Args:
        diffCoeff (float): diffusion coefficient in units of [V]
        cornerFreq (float): corner frequency in units of [Hz]
        viscosity (float): viscosity in units of [pN s / nm²]
        beadDiameter (float): bead radius in units of [nm]
        temperature (float): temperature in units of ˚C

    Returns:
        two :class:`dict` for data and units with keys:
        `stiffness` in units of [pN/nm]
        `displacementSensitivity` in units of [V/nm]
        `forceSensitivity` in units of [V/pN]
    """

    beadRadius = beadDiameter / 2
    stiffness = trapStiffness(fc=cornerFreq, radius=beadRadius, viscosity=viscosity)
    dispSens = distanceCalibration(D=diffCoeff, radius=beadRadius, viscosity=viscosity, T=temperature)
    forceSens = dispSens * stiffness

    res = OrderedDict([('stiffness', stiffness),
                       ('displacementSensitivity', dispSens),
                       ('forceSensitivity', forceSens)])
    units = OrderedDict([('stiffness', 'pN/nm'),
                         ('displacementSensitivity', 'nm/V'),
                         ('forceSensitivity', 'pN/V')])

    return res, units

