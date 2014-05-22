import sys
import os
import numpy as np
from skimage import filter
from tkinter import *

try:
    from astropy.io import fits
except ImportError:
    import pyfits as fits

from tkinter.filedialog import askopenfilename


# distance between edges in nm
_SCALE = 10000


def get_edges(line, threshold=10):
    """
    Gets the edges coordinates from the whole line of the image and discriminate false edges

    Parameters
    ----------
    line : np.array
        a line in the image to count the number of edges

    threshold : int, optional
        Minimum distance in pixels between two actual edges
        Default : 10
        TODO: This is useful to remove false edges, but can be further optimized for more precision

    Returns
    -------
    edgesCoord : list of int
        Coordinates of the edges in the specified line.
        Removes the first element, set to 0 for loop purposes
    """

    edgesCoord = [0]
    for iPixel, pixel in enumerate(line):

        if int(pixel) == 1:
            if abs(edgesCoord[-1]-iPixel) < threshold:        # If two edges are closer than this number,
                edgesCoord[-1] = (edgesCoord[-1]+iPixel)/2    # the edge is considered to be the mean of the values
            else:
                edgesCoord.append(iPixel)

    return edgesCoord[1:]


def mean_edge_separation(edgesCoord):
    """
    average separation (between equivalent edges) of the three lines of each image
    It considers the distance between two equivalent edges (two indexes away in the list)
    
    Parameters
    ----------
    edgesCoord : list of int
        Coordinate (in pixel) of the edges in one line

    Returns
    -------
    meanOneLine : float
        average distance between edges in one line
    
    """

    meanOneLine = 0

    for iEdge in range(len(edgesCoord)-2):
        meanOneLine = meanOneLine + abs(edgesCoord[iEdge] - edgesCoord[iEdge + 2])
    if len(edgesCoord) - 2 == 0:    # if not enough edges were detected in the line
        meanOneLine = 0
    else:
        meanOneLine /= (len(edgesCoord) - 2)

    return meanOneLine


def check_orientation(edgesImage):
    """
    Function to determine the orientation of each image

    Parameters
    ----------
    edgesImage : np.array
        Image to be analyzed

    Returns
    -------
    orientation : int
        0 for horizontal, 1 for vertical and 2 for not determined

    """

    verLine = edgesImage[250:251, 1:512]        # Arbitrary vertical line
    horLine = edgesImage[81:512, 250:251]       # Arbitrary horizontal line
    verLine = verLine[0]                        # set correct format for the np.array

    vl = [int(x) for x in verLine]              # Transform to list of int
    hl = [int(x) for x in horLine]              # Transform to list of int

    if hl.count(1) > vl.count(1) or vl.count(1) > 20:
        orientation = 0
    elif hl.count(1) < vl.count(1) or hl.count(1)>20:
        orientation = 1
    elif hl.count(1) == vl.count(1):
        orientation = 2

    return orientation


def get_factor(edgesImage, orientation):
    """
    Function to get the nm/pixel factor by edge detection
    
    Parameters
    ----------
    edgesImage : np.array
        image containing the edge information

    Returns
    -------
    factor : float
        Distance calibration factor in units of nm/pixel
    """

    #plt.imshow(edges)
    #plt.show()

    # HORIZONTAL
    if orientation == 0:
        c1 = get_edges(edgesImage[81:512, 150:151])
        c2 = get_edges(edgesImage[81:512, 200:201])
        c3 = get_edges(edgesImage[81:512, 250:251])
        meanDistance = (mean_edge_separation(c1) +
                        mean_edge_separation(c2) +
                        mean_edge_separation(c3))/3
        if meanDistance != 0:
            factor = _SCALE/meanDistance
        else:
            factor = 0

    # VERTICAL
    elif orientation == 1:
        line1 = edgesImage[150:151, 1:512]
        c1 = get_edges(line1[0])
        line2 = edgesImage[200:201, 1:512]
        c2 = get_edges(line2[0])
        line3 = edgesImage[250:251, 1:512]
        c3 = get_edges(line3[0])
        meanDistance = (mean_edge_separation(c1) +
                        mean_edge_separation(c2) +
                        mean_edge_separation(c3))/3
        if meanDistance != 0:
            factor = _SCALE/meanDistance
        else:
            factor = 0

    # NOT POSSIBLE TO DETERMINE
    elif orientation == 2:
        factor = 0

    return factor


def eliminate_bad_factors(factorX, factorY, criterion=1):

    """
    Removes the factors that deviate to much from the mean

    Parameters
    ----------
    factorX, factorY : list of float
        Contain all the calculated distance calibration factors

    criterion : float
        How many standard deviations away from the mean the values can be
        Default : 1

    Returns
    -------
    factorX, factorY : lost of float
        Filtered list without values too deviated from the mean
    """

    # means and standard deviations of the factors
    mean = [np.mean(factorX), np.mean(factorY)]
    std = [np.std(factorX), np.std(factorY)]

    #elements to be eliminated
    removedElements = []

    for factor in factorX:
        if abs(factor-mean[0]) > criterion*std[0]:
            removedElements.append(factor)
    for element in removedElements:
        factorX.remove(element)

    #clear the list
    removedElements = []

    for element in factorY:
        if abs(element-mean[1]) > criterion*std[1]:
            removedElements.append(element)
    for element in removedElements:
        factorY.remove(element)

    return factorX, factorY


def factor_andor(fitsFile=os.path.dirname(os.path.realpath(__file__)), sigma_edge_filter=3):
    """
    Function to get the calibration factors from a .fits file generated by the ANDOR camera

    Parameters
    ----------
    fitsFile : str
        Sets the path to the .fits file

    sigma_edge_filter : float
        Threshold for the edge finding. In case of bad results, try changing this value
        Default: 3

    Returns
    -------
    np.mean(factorX), np.mean(factorY) : float
        Mean values of the X and Y distance calibration factors

    """
    nImages = fits.getheader(fitsFile)
    print("There are", nImages['NAXIS3'], "images in the file. It may take some minutes...")
    imageCollection = fits.getdata(fitsFile)

    # Values of the distance calibration factor
    factorX = []
    factorY = []    

    for indexImage, image in enumerate(imageCollection):

        # To show progress
        sys.stdout.write("\rProgress: %d%%" % int(indexImage*100/(len(imageCollection)-1)))
        sys.stdout.flush()

        # Remove black sections
        # image = image[40:550, 85:540]

        # Function from scikit-image to get edges
        edgesImage = filter.canny(image, sigma=sigma_edge_filter)


        # Get the orientation of the image
        orientation = check_orientation(edgesImage)

        # Get the distance calibration factor
        factor = get_factor(edgesImage, orientation)

        # Store the factor in the proper list (X or Y), only if it is not 0
        if orientation == 0 and factor != 0.0 and factor != -0.0:
            factorX.append(get_factor(edgesImage, orientation))
        elif orientation == 1 and factor != 0.0 and factor != -0.0:
            factorY.append(get_factor(edgesImage, orientation))

    # Eliminate wrong values
    factorX, factorY = eliminate_bad_factors(factorX, factorY)
    factorX, factorY = eliminate_bad_factors(factorX, factorY)

    # Print values on screen
    print("Calibration values for images in {}\n".format(fitsFile))
    print("X axis: {:.4f} +/- {:.3f} nm/pix\n".format(np.mean(factorX), np.std(factorX)))
    print("Y axis: {:.4f} +/- {:.3f} nm/pix\n".format(np.mean(factorY), np.std(factorY)))

    return np.mean(factorX), np.mean(factorY)
