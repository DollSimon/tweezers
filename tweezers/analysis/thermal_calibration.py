from collections import OrderedDict
from physics.tweezers import distance_calibration, trap_stiffness


def thermalCalibration(diffCoeff, cornerFreq, viscosity, beadDiameter, temperature=25):
    """
    Perform the thermal calibration for the given input parameters. This calculates the trap stiffness, displacement
    sensitivity and force sensitivity of the trap.

    Args:
        diffCoeff (float): diffusion coefficient in units of [V]
        cornerFreq (float): corner frequency in units of [Hz]
        viscosity (float): viscosity in units of [pN s / nm²]
        beadDiameter (float): bead diameter in units of [nm]
        temperature (float): temperature in units of ˚C

    Returns:
        two :class:`dict` for data and units with keys:
        `Stiffness` in units of [pN/nm]
        `DisplacementSensitivity` in units of [V/nm]
        `ForceSensitivity` in units of [V/pN]
    """

    radius = beadDiameter / 2
    stiffness = trap_stiffness(fc=cornerFreq, radius=radius, viscosity=viscosity)
    dispSens = distance_calibration(D=diffCoeff, radius=radius, viscosity=viscosity, T=temperature)
    forceSens = dispSens / stiffness

    res = OrderedDict([('stiffness', stiffness),
                       ('displacementSensitivity', dispSens),
                       ('forceSensitivity', forceSens)])
    units = OrderedDict([('stiffness', 'pN/nm'),
                         ('displacementSensitivity', 'V/nm'),
                         ('forceSensitivity', 'V/pN')])

    return res, units

