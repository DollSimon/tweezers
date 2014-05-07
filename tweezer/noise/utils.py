#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import print_function, division

import numpy as np

from tweezer.ixo.math_ import map_array_to_range


def generate_power_noise(alpha=1, nSamples=1e5, normalize=False,
                         deterministic_spectrum=True):
    """
    Generate samples of power law noise. The power spectrum
    of the signal scales as f^(-alpha).

    :param alpha: (number) scaling exponent for the power law
    :param nSamples: (int) number of samples to produce

    :param noramlize: (boolean) whether to map the resulting series to the
    range [-1, 1]
    :param deterministic_spectrum: (boolean) to switch between deterministic
    and stochastic distribution of power spectrum (see details)

    :return X: (numpy.array) of the signal whose frequency response follows
    the power law

    Details:
    --------

    |P(f)|^2 = 1/f^alpha. Special cases include 1/f noise (alpha = 1) and
    white noise (alpha = 0). The algorithm generates the appropriate Fourier
    domain sequence, with power-law spectral magnitudes and randomised phases.
    It then inverts this using the inverse FFT to generate the required time
    series. Note that, in order to cope with the degeneracy at f = 0, it sets
    the zero frequency component to an amplitude of 1. This guarantees power
    law scaling across the whole frequency range (right down to 0Hz), but the
    mean of the time series will not be exactly zero.

    With no option strings specified, the power spectrum is
    deterministic, and the phases are uniformly distributed in the range
    -pi to +pi. The power law extends all the way down to 0Hz (DC)
    component. By specifying the 'randpower' option (edit: by flipping the
        *deterministic_spectrum* flag) string however, the
    power spectrum will be stochastic with Chi-square distribution. The
    'normalize' option string forces scaling of the output to the range
    [-1, 1], consequently the power law will not necessarily extend
    right down to 0Hz.

    ..note::

        This is a Python port of the following code:

        If you use this code for your research, please cite [1].

        References:

        [1] M.A. Little, P.E. McSharry, S.J. Roberts, D.A.E. Costello, I.M.
        Moroz (2007), Exploiting Nonlinear Recurrence and Fractal Scaling
        Properties for Voice Disorder Detection, BioMedical Engineering OnLine
        2007, 6:23.

    """
    NYQ = int(np.floor((nSamples / 2) - 1))

    frequency = np.arange(2, NYQ + 2, dtype=int)

    ideal_spectrum = 1.0 / (frequency ** (alpha / 2.0))
    ideal_spectrum = ideal_spectrum.reshape((ideal_spectrum.size, 1))

    if deterministic_spectrum:
        fluctuations = (np.random.random(size=(NYQ, 1)) - 0.5) * 2 * np.pi
        real_spectrum = ideal_spectrum * np.exp(1j * fluctuations)
    else:
        fluctuations = np.random.random(size=(NYQ, 1)) + np.random.random(size=(NYQ, 1)) * 1j
        real_spectrum = ideal_spectrum * fluctuations

    full_spectrum = np.concatenate((np.array([[1]]),
                                    real_spectrum,
                                    np.array([[1.0 / ((NYQ + 2) ** alpha)]]),
                                    np.flipud(np.conjugate(real_spectrum))))

    X = np.real(np.fft.ifft(full_spectrum, axis=0))

    if normalize:
        X = map_array_to_range(X, [-1, 1])

    return X


def generate_lorentzian_power_noise(cornerFrequency=100,
                                    diffusionCoef=1,
                                    nSamples=5e5,
                                    normalize=False,
                                    deterministic_spectrum=True):

    fc = cornerFrequency
    D = diffusionCoef

    NYQ = int(np.floor((nSamples / 2) - 1))

    frequency = np.arange(2, NYQ + 2, dtype=int)

    ideal_spectrum = (D / (2 * np.pi)) / (fc ** 2 + frequency ** 2)
    ideal_spectrum = ideal_spectrum.reshape((ideal_spectrum.size, 1))

    if deterministic_spectrum:
        fluctuations = (np.random.random(size=(NYQ, 1)) - 0.5) * 2 * np.pi
        real_spectrum = ideal_spectrum * np.exp(1j * fluctuations)
    else:
        fluctuations = np.random.random(size=(NYQ, 1)) + np.random.random(size=(NYQ, 1)) * 1j
        real_spectrum = ideal_spectrum * fluctuations

    full_spectrum = np.concatenate((np.array([[1]]),
                                    real_spectrum,
                                    np.array([[(D / (2 * np.pi)) / (fc ** 2 + NYQ ** 2)]]),
                                    np.flipud(np.conjugate(real_spectrum))))

    X = np.real(np.fft.ifft(full_spectrum, axis=0))

    if normalize:
        X = map_array_to_range(X, [-1, 1])

    return X


if __name__ == '__main__':
    X = generate_power_noise(2, 1000)
