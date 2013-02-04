#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Contains classes and functions related to the calibration of forces in an optical trap
"""

import numpy as np

class SingleTrapPowerSpectrum(object):
    """
    Analytic form for fitting the power spectrum of a microsphere trapped in a single optical trap


    Parameter:
        D - diffusion_coefficient (µm^2 / s)
        fc - corner_frequency (500 Hz)

    Methods:
        constructor(L, P, S, T): set parameter (with default values)
        power_spectrum(frequency): compute the extension at a certain force
        formula(): print out formula used
    """
    def __init__(self, diffusion_coefficient, corner_frequency = 500):
        self.D = float(diffusion_coefficient)
        self.fc = float(corner_frequency)

    def __call__(self, frequency):

        f = float(frequency)

        PSD = self.D / (np.pi ** 2 * (self.fc ** 2 + f **2))

        return PSD

    def formula(self):
        return "PSD(f; D, fc) = D / π^2 * (fc^2 + f^2)"

