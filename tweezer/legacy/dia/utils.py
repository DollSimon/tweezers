#!/usr/bin/env python
#-*- coding: utf-8 -*-


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from astropy.io import fits


def show_images(images, titles=None):
    """Display a small list of images in a row"""
    n_ims = len(images)
    if titles is None:
        titles = ['(%d)' % i for i in range(1, n_ims + 1)]

    fig = plt.figure()
    n = 1
    for image, title in zip(images, titles):

        a = fig.add_subplot(1, n_ims, n)

        # Test if image is gray-scale
        if image.ndim == 2:
            plt.gray()

        plt.imshow(image)

        a.set_title(title)

        n += 1

    fig.set_size_inches(np.array(fig.get_size_inches()) * n_ims)

    plt.show()


class CameraConversionFactor(object):
    def __init__(self, camera='ccd'):
        self.camera = camera


def get_times_from_andor_fits(fileName):
    """
    Reads the time information from an Andor .fits file.

    :param: fileName
    :return: times
    """

    header = fits.getheader(fileName)

    # parse header
    startTime = header['FRAME']
    timePerFrame = header['KCT']
    nImages = header['NUMKIN']

    # create list of pandas time stamps
    times = [pd.to_datetime(startTime) + i * pd.to_timedelta(str(timePerFrame), unit='s') for i in range(nImages)]

    return times