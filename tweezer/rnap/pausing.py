#!/usr/bin/env python
#-*- coding: utf-8 -*-

import numpy as np
from scipy.special import i1


"""
Mainly based on the work of Martin Depken, Eric Galburt, Juan Parrondo and
Stephan Grill
"""


def pause_distribution(time, kf=1, kb=1):

    preFactor = np.sqrt(np.float(kf) / kb)
    midFactor = (np.exp(-(kf + kb) * time) / time)
    postFactor = i1(2 * time * np.sqrt(kf * kb))

    return preFactor * midFactor * postFactor


def pause_density():
    pass


def pause_free_velocity():
    pass


def forward_rate(force, k0, delta=0.17, kbT=4.11):
    return k0 * np.exp(force * delta / kbT)


def backward_rate(force, k0, delta=0.17, kbT=4.11):
    return k0 * np.exp(-force * (1 - delta) / kbT)


def Km(k1, k_1, k3, K):
    """
    Michaelis constant
    """
    return ((k1 + k_1) / (k1 + k3)) * K


def K(k_2, k2, k3):
    """
    Dimensionless constant
    """
    return (k_2 + k3) / k2
