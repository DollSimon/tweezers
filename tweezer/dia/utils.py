#!/usr/bin/env python
#-*- coding: utf-8 -*-


import matplotlib.pyplot as plt
import numpy as np


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
