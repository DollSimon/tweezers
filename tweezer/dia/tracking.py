#!/usr/bin/env python
#-*- coding: utf-8 -*-

import numpy as np

from skimage.filter import denoise_tv_chambolle, threshold_otsu, rank
from skimage.morphology import disk, label

from skimage.segmentation import clear_border
from skimage.measure import regionprops


def crop_frame(inputImg, bottomRowsToCrop=30):
    """
    Crops black margins in CCD images. Also crops bottom part that contains
    timing information from LabView

    Parameters:
    -----------
        inputImg: image from tweezer CCD camera (often with black margins)


    Returns:
    ---------
        outputImg: cropped image

        croppingFrame: mask used to crop
    """
    outputImg = inputImg.copy()

    print("Mean intensity: {}".format(np.mean(outputImg)))

    croppingFrame = np.zeros(outputImg.shape)
    firstRow = outputImg[1, ]

    cropCriteria = np.mean(outputImg) - np.sqrt(np.var(outputImg))

    almostBlackHere = np.where(firstRow < cropCriteria)

    # cut left and right if it is almost entirely black
    outputImg = np.delete(outputImg, almostBlackHere[0], axis=1)
    croppingFrame[:, np.where(firstRow < cropCriteria)] = 255

    nRowsToCrop = range(inputImg.shape[0] - bottomRowsToCrop,
                        inputImg.shape[0])

    outputImg = np.delete(outputImg, nRowsToCrop, axis=0)
    croppingFrame[nRowsToCrop, :] = 255

    return outputImg, croppingFrame


def find_regions(inputImg, denoisingWeight=0.1, sizeOfCircularMask=8):
    """
    Finds interesting regions in an image
    """

    outputImg = inputImg.copy()

    denoisedImg = denoise_tv_chambolle(outputImg, weight=denoisingWeight)

    kernelDisk = disk(sizeOfCircularMask)

    filteredImg = filter.rank.median(denoisedImg, kernelDisk)

    otsuThreshold = threshold_otsu(filteredImg)

    tempImg = filteredImg.copy()

    ostuImg = tempImg < otsuThreshold

    # remove anything touching the border
    outputImg = clear_border(ostuImg)

    return outputImg


def find_properties(inputImg, verbose=True):

    outputImg = inputImg.copy()

    labeledImg = label(outputImg)

    properties = regionprops(labeledImg)

    if verbose:
        print("Found {} interesting regions".format(len(properties)))

    return properties


def uncrop_image(croppedImg, croppingFrame):

    # check that size of croppedImg and croppingFrame interior match
    

    return combinedImg

