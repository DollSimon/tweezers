# coding=utf-8

__doc__ = """\
Thermal calibration of single optical trap.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tweezer.physics import thermal_energy


def corner_frequency(dragCoefficient=2e-5, trapStiffness=0.1, verbose=False):
    """
    Corner frequency of the spectrum of a single trap.

    Parameters
    ----------
    dragCoefficient : float
        Stokes drag coefficient in [pN/nm s]
        Default: 2e-5 pN/nm s

    trapStiffness : float
        Trap stiffness in [pN/nm]
        Default: 0.1 pN/nm

    verbose : bool
        Print parameters and results with units
        Default: False

    Returns
    -------
    cornerFrequency : float
        Characteristic frequency of the power spectrum in [Hz]

    """
    assert trapStiffness > 0
    assert dragCoefficient > 0

    cornerFrequency = trapStiffness / (2 * np.pi * dragCoefficient)

    if verbose:
        print("In:")
        print("Drag coefficient: gamma = {} pN/nm s".format(round(dragCoefficient, 12)))
        print("Trap stiffness: k = {} pN/nm^2 s\n".format(trapStiffness))

        print("Out:")
        print("Corner frequency: fc = {} Hz\n".format(cornerFrequency))

    return cornerFrequency


def trap_stiffness(cornerFrequency=500, dragCoefficient=2e-5, verbose=False):
    """
    Trap stiffness of a single trap from the corner frequency of the power spectrum.

    Parameters
    ----------
    cornerFrequency : float
        Characteristic frequency of the power spectrum in [Hz]
        Default: 500 Hz

    dragCoefficient : float
        Stokes drag coefficient in [pN/nm s]
        Default: 2e-5 pN/nm s

    verbose : bool
        Print parameters and results with units
        Default: False

    Returns
    -------
    trapStiffness : float
        Trap stiffness in [pN/nm]

    """
    assert cornerFrequency > 0
    assert dragCoefficient > 0

    trapStiffness = 2 * np.pi * cornerFrequency * dragCoefficient

    if verbose:
        print("In:")
        print("Corner frequency: fc = {} Hz\n".format(cornerFrequency))
        print("Drag coefficient: gamma = {} pN/nm s".format(round(dragCoefficient, 12)))

        print("Out:")
        print("Trap stiffness: k = {} pN/nm^2 s\n".format(trapStiffness))

    return trapStiffness


def detector_sensitivity(diffusionConstant=0.12, dragCoefficient=2e-9, thermalEnergy=thermal_energy(), verbose=False):
    """
    Detector sensitivity used for the position calibration of an optical trap.

    Parameters
    ----------
    diffusionConstant : float
        Diffusion constant in [pN/nm]
        Default: 2 pN/nm

    dragCoefficient : float
        Stokes drag coefficient in [pN/nm s]
        Default: 2e-5 pN/nm s

    verbose : bool
        Print parameters and results with units
        Default: False

    Returns
    -------
    detectorSensitivity : float
        Distance calibration factor (beta) in units of [V/nm]

    """
    assert diffusionConstant > 0
    assert dragCoefficient > 0
    assert thermalEnergy > 0

    detectorSensitivity = 1 / np.sqrt(thermalEnergy / dragCoefficient * diffusionConstant)

    if verbose:
        print("In:")
        print("Diffusion coefficient: D = {} V^2/s".format(round(diffusionConstant, 12)))
        print("Thermal energy: kbT = {} pN nm".format(round(thermalEnergy, 12)))
        print("Drag coefficient: gamma = {} pN/nm s\n".format(round(dragCoefficient, 12)))

        print("Out:")
        print("Detector sensitivity: beta = {} V/nm\n".format(detectorSensitivity))

    return detectorSensitivity


def power_spectrum_mpl(data, asDataFrame=True):
    """
    Calculates the power spectral density

    Parameter
    ---------
    data : array

    """
    psd, freq = plt.psd(data, NFFT=block, Fs=sampling_rate, noverlap=overlap)

    if asDataFrame:
        psdData = pd.DataFrame({'freq': freq, 'psd': psd})
        return psdData
    else:
        return psd, freq


def positional_fluctuations(kBT=thermal_energy(), trapStiffness=0.02):
    """
    Average measure for the position fluctuations of a bead in an optical trap.
    """
    return np.sqrt(kBT / trapStiffness)


def mle_factors(frequency, powerSpectrum, asMatrix=True):
    """
    Calculation of the S coefficients related to the MLE, according to the paper of Norrelykke et al.

    Parameters
    ----------
    frequency : numpy.array
        Frequency in [Hz]

    powerSpectrum : numpy.array
        Experimental PSD function in [V^2]

    asMatrix : bool
        Whether to return factor as numpy.matrix. If 'False' a nested list is returned
        Default: True

    Returns
    -------
    S : numpy.matrix
        Matrix with the S coefficients

    .. [1] Power spectrum analysis with least-squares fitting: Amplitude biasand its elimination, with \
    application to optical tweezers and atomic force microscope cantilevers. 1–16 (2010). doi:10.1063/1.3455217
    """
    assert len(frequency) == len(powerSpectrum)

    observations = len(frequency)

    s00 = 0
    s01 = 1 / (observations) * np.sum(powerSpectrum)
    s02 = 1 / (observations) * np.sum(np.power(powerSpectrum, 2))

    s10 = 0
    s11 = 1 / (observations) * np.sum(np.multiply(np.power(frequency, 2), powerSpectrum))
    s12 = 1 / (observations) * np.sum(np.multiply(np.power(frequency, 2), np.power(powerSpectrum, 2)))

    s20 = 0
    s21 = s12
    s22 = 1 / (observations) * np.sum(np.multiply(np.power(frequency, 4), np.power(powerSpectrum, 2)))

    S = [[s00, s01, s02],
         [s10, s11, s12],
         [s20, s21, s22]]

    if asMatrix:
        S = np.matrix(S)

    return S


def mle_prefactors(S):
    """
    Calculates pre-parameters a and b from the mle statistic S

    Routine used by Norrelykke et al. to calibrate the power spectrum of an optical trap in an unbiased way.

    Parameter
    ---------
    S : numpy.matrix
        Matrix with MLE coefficients; special statistic calculated from the experimental power spectrum

    Returns
    -------
    a : float
        Pre-parameter for the calculation of D and fc

    b : float
        Pre-parameter for the calculation of D and fc

    .. [1] Power spectrum analysis with least-squares fitting: Amplitude biasand its elimination, with application
    to optical tweezers and atomic force microscope cantilevers. 1–16 (2010). doi:10.1063/1.3455217
    """
    if isinstance(S, np.matrix):
        a1 = (S[0, 2] * S[2, 2] - S[1, 2] * S[1, 2])
        a2 = (S[0, 1] * S[2, 2] - S[1, 1] * S[1, 2])

        a = 1 / a1 * a2

        b1 = (S[0, 2] * S[2, 2] - S[1, 2] * S[1, 2])
        b2 = (S[1, 1] * S[0, 2] - S[0, 1] * S[1, 2])

        b = 1 / b1 * b2

    elif isinstance(S, list):
        a1 = (S[0][2] * S[2][2] - S[1][2] * S[1][2])
        a2 = (S[0][1] * S[2][2] - S[1][1] * S[1][2])

        a = 1 / a1 * a2

        b1 = (S[0][2] * S[2][2] - S[1][2] * S[1][2])
        b2 = (S[1][1] * S[0][2] - S[0][1] * S[1][2])

        b = 1 / b1 * b2

        # a = 1/(S[0][2]*S[2][2]-S[1][2]*S[1][2])*(S[0][1]*S[2][2]-S[1][1]*S[1][2])
        # b = 1/(S[0][2]*S[2][2]-S[1][2]*S[1][2])*(S[1][1]*S[0][2]-S[0][1]*S[1][2])

    else:
        raise TypeError("Can't figure out what to do with S of type {}".format(type(S)))

    return a, b


def mle_parameters(a, b):
    """Calculate parameters from the factors of the MLE

    Args:
        a, b (float): pre-parameters for the calculation of D and fc

    Returns:
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]

    """
    if a * b > 0:
        fc = np.sqrt(a / b)
    else:
        fc = 0

    D = 2 * np.pi ** 2 / b

    return D, fc
