from collections import OrderedDict
import numpy as np

import tweezers.physics.thermodynamics as thermo
import tweezers.physics.hydrodynamics as hydro


def thermalCalib(cornerFreq, diffCoef, beadDiameter, viscosity, temperature=25.0):
    """
    Perform the thermal calibration for the given input parameters. This calculates the stiffness, displacement
    sensitivity and force sensitivity of the trap.

    Args:
        cornerFreq (`float`): corner frequency in units of [Hz]
        diffCoef (`float`): diffusion coefficient in units of [V]
        beadDiameter (`float`): bead radius in units of [nm]
        viscosity (`float`): viscosity in units of [pN s / nm²]
        temperature (`float`): temperature in units of ˚C

    Returns:
        two :class:`dict` for data and units with keys:
        `stiffness` in units of [pN/nm]
        `displacementSensitivity` in units of [V/nm]
        `forceSensitivity` in units of [V/pN]
    """

    beadRadius = beadDiameter / 2
    dragCoef = hydro.dragSphere(beadRadius, viscosity)
    res, units = thermalCalibDrag(cornerFreq, diffCoef, dragCoef, temperature=temperature)

    return res, units


def thermalCalibDrag(cornerFreq, diffCoef, dragCoef, temperature=25.0):

    dispSens = np.sqrt(thermo.kbt(temperature) / (dragCoef * diffCoef))
    stiffness = 2 * np.pi * cornerFreq * dragCoef
    forceSens = dispSens * stiffness

    res = OrderedDict([('stiffness', stiffness),
                       ('displacementSensitivity', dispSens),
                       ('forceSensitivity', forceSens),
                       ('dragCoef', dragCoef)])
    units = OrderedDict([('stiffness', 'pN/nm'),
                         ('displacementSensitivity', 'nm/V'),
                         ('forceSensitivity', 'pN/V'),
                         ('dragCoef', 'pN s / nm')])

    return res, units


def thermalCalibOsci(cornerFreq, diffCoef, driveFreq, amplitude, driveFreqPower, temperature=25.0):
    """
    Perform the thermal calibration using the oscillation method for the given input parameters. This calculates the
    stiffness, displacement sensitivity and force sensitivity of the trap as well as the drag coefficient of the bead.

    Args:
        cornerFreq (`float`): corner frequency in units of [Hz]
        diffCoef (`float`): diffusion coefficient in units of [V]
        driveFreq (`float`):
        driveFreqPower (`float`):
        temperature (`float`): temperature in units of ˚C

    Returns:
        two :class:`dict` for data and units with keys:
        `stiffness` in units of [pN/nm]
        `displacementSensitivity` in units of [V/nm]
        `forceSensitivity` in units of [V/pN]
        `dragCoef` in units of pN s / nm
    """

    wth = wTh(amplitude, cornerFreq, driveFreq)
    wexp = driveFreqPower

    dispSens = np.sqrt(wth / wexp)
    dragCoef = thermo.kbt(temperature) / (dispSens**2 * diffCoef)
    stiffness = 2 * np.pi * cornerFreq * dragCoef
    forceSens = dispSens * stiffness

    res = OrderedDict([('wExp', wexp),
                       ('wTh', wth),
                       ('stiffness', stiffness),
                       ('displacementSensitivity', dispSens),
                       ('forceSensitivity', forceSens),
                       ('dragCoef', dragCoef)])
    units = OrderedDict([('stiffness', 'pN/nm'),
                         ('displacementSensitivity', 'nm/V'),
                         ('forceSensitivity', 'pN/V'),
                         ('dragCoef', 'pN s / nm')])

    return res, units


def wTh(amplitude, cornerFreq, driveFreq):
    wth = amplitude ** 2 / (2 * (1 + (cornerFreq / driveFreq) ** 2))
    return wth


def wExp(psdOsci, psdFit, driveFreq):
    """
    Calculate the experimentally measured power at the driving frequency from the power spectrum and its fit. This is
    required for the oscillation calibration method.

    Args:
        psdOsci (:class:`numpy.ndarray`): experimental PSD with first column frequencies and second column PSD values
        psdFit (:class:`numpy.ndarray`): PSD fit with first column frequencies and second PSD fit values
        driveFreq (`float`):

    Returns:
        `float`
    """

    # get frequencies
    f = psdOsci[:, 0]
    # get all frequencies as integers for comparison
    # this is required for cases where driveFreq is not an integer to ensure comparison still works
    # however it requires that df > 1
    fInt = f.astype(int)
    driveFreqInt = int(driveFreq)
    fFitInt = psdFit[:, 0].astype(int)
    # get peak value
    pPeak = psdOsci[fInt == driveFreqInt, 1][0]
    # get background value
    pBackground = psdFit[fFitInt == driveFreqInt, 1][0]
    # get frequency resolution
    df = f[1] - f[0]
    return (pPeak - pBackground) * df


def doThermalCalib(t, trap):
    """
    Perform the thermal calibration on the given trap of the :class:`tweezers.TweezersData`. Calibration results are
    stored in the object.

    For the oscillation calibration, note that the oscillating trap axis (e.g. y) must be calibrated first to calculate
    the drag coefficent from the calibration. This is used to calibrate the other axis (e.g. x).

    Args:
        t (:class:`tweezers.TweezersData`): data object
        trap (`str`): trap name to calibrate

    Returns:
        :class:`tweezers.TweezersData`
    """

    trapMeta = t.meta[trap]

    if t.meta.psdType == 'normal':
        # convert diameter to nm (likely given in µm)
        if t.units[trap]['beadDiameter'] == 'nm':
            diam = trapMeta['beadDiameter']
        elif t.units[trap]['beadDiameter'] in ['um', 'µm']:
            diam = trapMeta['beadDiameter'] * 1000
        else:
            raise ValueError('Unknown bead radius unit encountered.')

        # do calibration
        res, units = thermalCalib(trapMeta.cornerFrequency, trapMeta.diffusionCoefficient, diam,
                                  t.meta.viscosity, temperature=t.meta.temperature)

    elif t.meta.psdType == 'oscillation':
        if trap.lower().endswith('y'):
            # calculate experimental power in oscillation peak
            driveFreq = t.meta.psdOscillateFrequency
            wex = wExp(t.psd[['f', trap]].values, t.psdFit[['f', trap]].values, driveFreq)

            # do calibration
            res, units = thermalCalibOsci(trapMeta.cornerFrequency, trapMeta.diffusionCoefficient,
                                          driveFreq, t.meta.psdOscillateAmplitude, wex,
                                          temperature=t.meta.temperature)
        else:
            yTrap = t.meta.getTrapAsY(trap)
            # do calibration
            res, units = thermalCalibDrag(trapMeta.cornerFrequency, trapMeta.diffusionCoefficient,
                                          t.meta[yTrap].dragCoef, temperature=t.meta.temperature)

    else:
        raise(ValueError('Unknown PSD type'))

    t.meta[trap].update(res)
    t.units[trap].update(units)
    return t
