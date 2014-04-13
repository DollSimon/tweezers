#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

from PyOCL import OCLProcessor
from numpy import *


from tweezer import _ROOT


def bilat(dev, data, width=20, beta=10, Niter=1):
    """
    Applies a bilateral filter given as 'bilateral' in pwc_kernels.cl to data
    width - filter size
    beta  - inverse filter strength

    Author: Martin Weigert, Myers-Lab, MPI-CBG
    """

    proc = OCLProcessor(dev, os.path.join(_ROOT, "kernel", "pwc_kernel.cl"))

    bufOut = dev.createBuffer(data.size, dtype=float32)
    bufIn = dev.createBuffer(data.size, dtype=float32)

    x = data[:]

    for i in range(Niter):
        dev.writeBuffer(bufIn, x.astype(float32))

        proc.runKernel("bilateral", (data.size,), None, bufIn, bufOut,
                       int32(data.shape[0]), int32(width), float32(beta))

        x = dev.readBuffer(bufOut, dtype=float32).reshape(data.shape)

    return x


def get_root_r():
    return _ROOT
