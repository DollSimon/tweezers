# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import math
from tweezer.physics import thermal_energy, drag_sphere as dg_sph, dynamic_viscosity_of_mixture, as_Kelvin
from tweezer.simulate.trap import *
import pandas as pd
from scipy.signal import welch
from collections import namedtuple
from scipy.optimize import curve_fit

def read_time_series(file, headerLines=6, columns=[1, 3], type="pandas"):
    """
    Reads a .txt file to obtain the data using pandas. It gets the columns specified in usecols and ignors the lines
    specified by header.

    Args:
        file (str): name of the file containing the data
        headerLines (int): number of lines of the header (Default: 7)
        columns (list of int): index of the columns to be read
        type (str): returns the data in pandas or numpy (Default: "pandas")

    Returns:
        data: returns the columns specified in usecols
    """

    if type == "pandas":
        data = pd.read_csv(file, usecols=columns, header=headerLines, sep=r"\t+")
        data.dropna(how="all", inplace=True)
        if columns == [1, 3]:
            data.columns = ['pm', 'aod']
        elif columns == [0, 1, 2, 3]:
            data.columns = ['pmx', 'pmy', 'aodx', 'aody']
        else:
            raise ValueError

    elif type == "numpy":
        columnsNumpy = (columns[0], columns[1])
        data = np.loadtxt(file, delimiter="\t", usecols=columnsNumpy, skiprows=headerLines, unpack=True)

    return data


def lorentzian(f, D, fc):
    """
    Lorentzian function

    Args:
        f (numpy.array): frequency in units of [Hz]
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]

    Returns:
        Lorentzian values(np.array): Lorentzian function with the corresponding parameters
    """

    return D/(math.pi**2*(f**2 + fc**2))


def distance_calibration(D=0.46, radius=1000, viscosity=8.93e-10, T=25):
    """Distance calibration factor (beta) in units of [V/nm]

    Args:
        D (float): diffusion constant in units of [V]
        radius (float): radius of the bead in units of [nm]
        viscosity (float): viscosity of the solution in units of [pN/nm^2s]
        T (float): temperature in units of [ºC]

    Returns:
        beta (float): distance calibration factor in units of [V/nm]
    """

    beta = 1/np.sqrt(thermal_energy(as_Kelvin(T))/(dg_sph(radius, viscosity)*D))

    return beta


def trap_stiffness(fc=500, radius=1000, viscosity=8.93e-10):
    """Trap stiffness in units of [pN/nm]

    Args:
        fc (float): corner frequency in units of [Hz]
        radius (float): radius of the bead in units of [nm]
        viscosity (float): viscosity of the solution in units of [pN/nm^2s]

    Returns:
        kappa (float): trap stiffness in units of [pN/nm]
    """

    kappa = 2*math.pi*fc*dg_sph(radius, viscosity)

    return kappa


def force_calibration(beta, kappa):
    """force calibration factor in units of [pN/V]

    Args:
        beta (float): distance calibration factor in units of [V/nm]
        kappa (float): trap stiffness in units of [pN/nm]

    Returns:
        alpha (float): force calibration factor in units of [pN/V]
    """

    alpha = kappa/beta

    return alpha


def lstsq_calibration(f,psd):
    result, errors = curve_fit(lorentzian, f, psd, p0=[0.0001, 500])
    
    if result[1] < 0:
        result[1] = -result[1]

    # standard deviation errors
    errors = np.sqrt(np.diag(errors))
    
    D=result[0]
    fc=result[1]
    chiSqr = residuals(f, psd, D, fc)
    return D, fc, errors, chiSqr


def mle_factors(f, P):
    """
    Calculation of the S coefficients related to the MLE, according to the paper of Norrelike

    Args:
        f (np.array): Frequency in [Hz]
        P (np.array): Experimental PSD function in [V^2]

    Returns:
        s (list of float): matrix with the S coefficients
    """
    s01 = 1/(len(f)) * np.sum(P)
    s02 = 1/(len(f)) * np.sum(np.power(P, 2))
    s11 = 1/(len(f)) * np.sum(np.multiply(np.power(f, 2), P))
    s12 = 1/(len(f)) * np.sum(np.multiply(np.power(f, 2), np.power(P, 2)))
    s22 = 1/(len(f)) * np.sum(np.multiply(np.power(f, 4), np.power(P, 2)))
    s = [[0, s01, s02], [0, s11, s12], [0, s12, s22]]

    return s


def mle_ab(s, n):
    """
    Calculation of the pre-parameters a and b, according to the paper of Norrelike

    Args:
        s (list of float): matrix with the S coefficients
        n (float): number of averaged power spectra (total data points divided by the block length)

    Returns:
        a, b (float): pre-parameters for the calculation of D and fc
    """

    a = ((1+1/n)/(s[0][2]*s[2][2]-s[1][2]*s[1][2])) * (s[0][1]*s[2][2]-s[1][1]*s[1][2])
    b = ((1+1/n)/(s[0][2]*s[2][2]-s[1][2]*s[1][2])) * (s[1][1]*s[0][2]-s[0][1]*s[1][2])
    return a, b


def mle_parameters(a, b, n):
    """Calculate parameters from the factors of the MLE

    Args:
        a, b (float): pre-parameters for the calculation of D and fc
        n (float): number of averaged power spectra (total data points divided by the block length)

    Returns:
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]

    """

    if a*b > 0:
        fc = math.sqrt(a/b)
    else:
        fc = 0
    D = (n * (math.pi)**2/(n+1)) / b

    return D, fc


def mle_errors(f, D, fc, a, b, n):
    """Function to get the standard deviation of the parameters according to the paper of Norrelyke

    Args:
        f (np.array): array of the frequencies in units of [Hz]
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]
        a, b (float): pre-parameters for the calculation of D and fc
        n (float): number of averaged power spectra (total data points divided by the block length)

    Returns:
        errosMle (np.array): with sigma(D) and sigma(fc)
    """
    y = lorentzian(f, D, fc)
    s = mle_factors(f, y)
    sB = [[(n+1)/n*s[0][2], (n+1)/n*s[1][2]], [(n+1)/n*s[1][2], (n+1)/n*s[2][2]]]
    sError = 1/(len(f)*n)*(n+3)/n*np.linalg.inv(sB)

    sigmaFc = fc**2/4 * (sError[0][0]/a**2+sError[1][1]/b**2-2*sError[0][1]/(a*b))
    sigmaD = D**2*(sError[1][1]/b**2)
    errorsMle = [np.sqrt(sigmaD), np.sqrt(sigmaFc)]

    return errorsMle


def mle_calibration(f, psd, n):
    """Calculates the diffusion constant in units of [V] and the corner frequency in units of [Hz] from the PSD,
    following the linear approximation of Norrelyke paper

    Args:
        f (pandas.DataFrame): frequency in units of [Hz]
        psd (pandas.DataFrame): PSD in units of [V^2]
        n (float): number of averaged power spectra (total data points divided by the block length)

    Returns:
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]
        errors (list of float): standard deviation of D and fc
        chiSqr (float): average of the squared residues (test of chi^2)
    """

    s = mle_factors(f, psd)
    a, b = mle_ab(s, n)
    D, fc = mle_parameters(a, b, n)

    errors = mle_errors(f, D, fc, a, b, n)
    chiSqr = residuals(f, psd, D, fc)

    return D, fc, errors, chiSqr


def residuals(f, psdExp, D, fc):
    """Performs a chi^2 test with the average of the residuals squared to test the best fitting limits

    Args:
        f (np.array): array of the frequencies in units of [Hz]
        psdExp (np.array): array of the experimental values of the PSD in units of [V^2]
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]
    Returns:
        np.mean(res) (float): the mean of the residuals squared
    """

    psdTheo = lorentzian(f, D, fc)
    res = [(exp-theo)**2 for exp, theo in zip(psdExp, psdTheo)]

    return np.mean(res)


def calculate_psd(data, blockLength=2**14, sFreq=80000, overlap=0):
    """Calculates the power spectral density of the data and sets the proper pandas format

    Args:
        data (pandas.DataFrame): data read from the file
        blockLength (float): length of each block of the time series taken for calculating the psd
        sFreq (float): sample frequency in units of [Hz]
        overlap (float): number of points for overlapping blocks

    Returns:
        psd (pandas.DataFrame): power spectrum density of the data
    """

    fRaw, psdRaw = welch(data, nperseg=blockLength, fs=sFreq, noverlap=overlap)

    #set format to pandas
    psd = pd.DataFrame({"psd": psdRaw, "f": fRaw})

    return psd


def single_calibration(psd, limit, n, plot=False, mode="mle"):
    """Calculates the Power Spectrum Density function of data, fits it with Maximum Likelihood Method (according to
    the reference given), and calculates the Diffusion constant [V] and the corner frequency [Hz]

    Args:
        psd (pandas.DataFrame): frequency in [Hz] and power spectrum density in [V^2]
        limit (list of int): sets the minimum and maximum frequency to be considered in the fit
        n (float): number of averaged power spectra (total data points divided by the block length)
        plot (bool): when True, it plots the PSD and the fit (Default: False)

    Returns:
        D (float): diffusion constant in units of V
        fc (float): corner frequency in units of Hz
        errors (list of float): standard deviation of the parameters
        chiSqr (float): average of the squared residues (test of chi^2)

    """
    
    #eliminate the points out of the limit range
    fLim = psd["f"][int(limit[0]):int(limit[1])]
    pLim = psd["psd"][int(limit[0]):int(limit[1])]

    #calculate parameters from data
    if(mode=="mle"):
        D, fc, errors, chiSqr = mle_calibration(fLim, pLim, n)
    elif(mode=="lstsq"):
        D, fc, errors, chiSqr = lstsq_calibration(fLim, pLim)

    #plot data and fit
    if plot == True:

        y = [lorentzian(x, D, fc) for x in fLim]
        plt.plot(psd["f"], psd["psd"])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('PSD (V^2)')

        plt.plot(fLim, y, color='orange', label='Maximum likelihood by S factors')

        plt.yscale('log')
        plt.xscale('log')
        plt.show()

    return D, fc, errors, chiSqr


def calibration_psd(psd, viscosity=8.93e-10, T=25, radius=1000, blockLength=2**14, TSLength=2**19, overlap=0, maxLim=0.6, plot=False, mode="mle"):
    """Performs the fitting of a PSD with different limits and chooses the
    one with least deviation (minimum mean residuals squared)

    Args:
        psd (pandas.DataFrame): PSD data
        viscosity (float): viscosity of the solution in units of [pN/nm^2s] (Default: 8.93e-10, pure water at 25 ºC)
        T (float): temperature in ºC
        radii (list of float): radius of the bead in units of [nm] (Default: [1000, 1000] nm)
        blockLength (float): length of each block of the time series taken for calculating the psd
        TSLength (float): total number of data points in the time series
        overlap (float): number of points for overlapping blocks
        maxLim (float): the minimum value of the psd multiplied by maxLim gives the maximum value considered for the fit
        plot (bool): if True, the fittings are plotted. Default: False

    Returns:
        fitPsd (named tuple): values of the fit: diffusion constant (D), corner frequency (fc), \
        errors of D and fc (sigma), distance calibration factor (beta), trap stiffness (kappa), \
        error of beta (eBeta), error of kappa (eKappa) and limits of the fit (limits)

    """

    #maxThreshold controls the maximum value for the limit as (minimum_value_of_PSD)*maxThreshold.
    # 1 takes the whole spectrum
    maxThreshold = min(psd["psd"])+10**(np.log10(min(psd["psd"]))-(-np.log10(psd["psd"][0])+np.log10(min(psd["psd"])))*maxLim)
    #set the first step as the fraction (points_in_limits_range)/stepInitial
    stepInitial = 5
    #set the precision criteria (in %) required to stop the iteration
    precision = 5

    #calculate the number of averaged spectra (nBlocks)
    if overlap == 0:
        nBlocks = TSLength/blockLength
    else:
        nBlocks = TSLength/blockLength*overlap


    #Maximum value considered in the fit
    limMax = next(a[0] for a in enumerate(psd["psd"]) if a[1] < maxThreshold)
    # minimum value considered in the fit
    limMin = next(a[0] for a in enumerate(psd['f']) if a[1] > 0)

    #starting limit is the maximum limit
    limits = [limMin, limMax]
    #the first step is taken in the negative direction
    step = -limMax//stepInitial

    D, fc, sigma, chiSqr = single_calibration(psd, limit=limits, n=nBlocks, mode=mode)
    D, fc, sigma, chiSqrNext = single_calibration(psd, limit=[limits[0], limits[1] + step], n=nBlocks, mode=mode)

    while abs((chiSqr-chiSqrNext)/chiSqr)*100 > precision:

        chiSqrNext = chiSqr
        D, fc, sigma, chiSqr = single_calibration(psd, limit=[limits[0], limits[1] + step], n=nBlocks, mode=mode)

        #iteration algorithm: after a step is made, if the fit is better (chiSqr is smaller) a new, smaller step in the
        #same direction is made ONLY if it will not go out of the maximum limit.
        #If some of the conditions fail, the step is made in the opposite direction
        if chiSqr < chiSqrNext and limits[1] <= limMax and limits[1]+step <= limMax:
            step = step//1.2
        else:
            step = -step//1.25

        limits[1] += step

    #evaluate the final result in case the user wants to plot
    D, fc, sigma, chiSqr = single_calibration(psd, limits, nBlocks, plot, mode)

    beta = distance_calibration(D, radius, viscosity, T)
    kappa = trap_stiffness(fc, radius, viscosity)
    eBeta = (sigma[0]/D)*beta
    eKappa=(sigma[1]/fc)*kappa


    Fit = namedtuple("Fit", ["D", "fc", "sigma", "beta", "kappa", "eBeta", "eKappa", "limits"])
    fitPsd = Fit(D, fc, sigma, beta, kappa, eBeta, eKappa, limits)
    return fitPsd


def calibration_time_series(data, viscosity=8.93e-10, T=25, radius=1000, blockLength=2**14, sFreq=80000, overlap=0, maxLim=0.6, plot=False, mode="mle"):
    """Performs the fitting with different limits from the time series data

    Args:
        data (pandas.DataFrame): data read from the file
        viscosity (float): viscosity of the solution in units of [pN/nm^2s] (Default: 8.93e-10, pure water at 25 ºC)
        T (float): temperature in ºC
        radii (list of float): radius of the bead in units of [nm] (Default: [1000, 1000] nm)
        blockLength (float): length of each block of the time series taken for calculating the psd
        sFreq (float): sample frequency in units of [Hz]
        overlap (float): number of points for overlapping blocks
        maxLim (float): the minimum value of the psd multiplied by maxLim gives the maximum value considered for the fit
        plot (bool): if True, the fittings are plotted. Default: False

    Returns:
        fitPsd (named tuple): values of the fit: diffusion constant (D), corner frequency (fc), \
        errors of D and fc (sigma), distance calibration factor (beta), trap stiffness (kappa), \
        error of beta (eBeta), error of kappa (eKappa) and limits of the fit (limits)

    """

    #calculation of the power spectrum density function with the Welch algorithm
    psd = calculate_psd(data, blockLength, sFreq, overlap)


    fit = calibration_psd(psd, viscosity, T, radius, blockLength, len(data), overlap, maxLim, plot, mode)

    return fit



def calibration_file(file, headerLines=7, columns=[0,1,2,3], type="pandas", viscosity=8.93e-10, T=25, radii=[1000,
                                                                                                             1000],
                     blockLength=2**14, sFreq=80000, overlap=0, maxLim=0.6, plot=False, mode="lstsq"):
    """Perform the thermal calibration from a time series file

    Args:
        file (str): name of the file containing the data
        headerLines (int): number of lines of the header (Default: 7)
        columns (list of int): index of the columns to be read (Default: [1,3] for Y direction PM and AOD)
        type (str): returns the data in pandas or numpy (Default: "pandas")
        viscosity (float): viscosity of the solution in units of [pN/nm^2s] (Default: 8.93e-10, pure water at 25 ºC)
        T (float): temperature in ºC
        radii (list of float): radius of the bead in units of [nm] (Default: [1000, 1000] nm)
        blockLength (float): length of each block of the time series taken for calculating the psd (Default: 2^14)
        sFreq (float): sample frequency in units of [Hz] (Default: 80000 Hz)
        overlap (float): number of points for overlapping blocks (Default: 0)
        maxLim (float): the minimum value of the psd multiplied by maxLim gives the maximum value considered for the fit
        plot (bool): if True, the fittings are plotted. (Default: False)

    Returns:
        fitPsd (named tuple): values of the fit: diffusion constant (D), corner frequency (fc), \
        errors of D and fc (sigma), distance calibration factor (beta), trap stiffness (kappa), \
        error of beta (eBeta), error of kappa (eKappa) and limits of the fit (limits)
    """

    #define arrays to store the fittting values
    D = []
    fc = []
    sigma = []
    beta =[]
    kappa = []
    eBeta = []
    eKappa = []
    limit = []

    #read data from file
    data = read_time_series(file, headerLines, columns, type)

    #Set the radius to be used
    for i, column in data.iteritems():
        if "pm" in i:
            rIndex = 0
        else:
            rIndex = 1

        fitTimeSeries = calibration_time_series(column, viscosity, T, radii[rIndex], blockLength, sFreq, overlap, maxLim, plot, mode)
        D.append(fitTimeSeries.D)
        fc.append(fitTimeSeries.fc)
        sigma.append(fitTimeSeries.sigma)
        beta.append(fitTimeSeries.beta)
        kappa.append(fitTimeSeries.kappa)
        eBeta.append(fitTimeSeries.eBeta)
        eKappa.append(fitTimeSeries.eKappa)
        limit.append(fitTimeSeries.limits)

    if len(columns) is 4:
        Fit = namedtuple("Fit", ["pm", "aod"])
        Fitpm = namedtuple("Fitpm", ["x", "y"])
        Fitaod = namedtuple("Fitaod", ["x", "y"])
        Fitpmx = namedtuple("Fitpmx", ["D", "fc", "sigma", "beta", "kappa",  "errorBeta", "errorKappa", "limits"])
        Fitpmy = namedtuple("Fitpmy", ["D", "fc", "sigma", "beta", "kappa",  "errorBeta", "errorKappa", "limits"])
        Fitaodx = namedtuple("Fitaodx", ["D", "fc", "sigma", "beta", "kappa",  "errorBeta", "errorKappa", "limits"])
        Fitaody = namedtuple("Fitaody", ["D", "fc", "sigma", "beta", "kappa",  "errorBeta", "errorKappa", "limits"])
        fitpmx = Fitpmx(D[0], fc[0], sigma[0], beta[0],
                       kappa[0], eBeta[0], eKappa[0],
                       limit[0])
        fitpmy = Fitpmy(D[1], fc[1], sigma[1],beta[1],
                kappa[1], eBeta[1], eKappa[1],
                limit[1])
        fitaodx = Fitaodx(D[2], fc[2], sigma[2], beta[2],
                        kappa[2], eBeta[2], eKappa[2],
                        limit[2])
        fitaody = Fitaody(D[3], fc[3], sigma[3], beta[3],
                kappa[3], eBeta[3], eKappa[3],
                limit[3])

        fitpm = Fitpm(fitpmx, fitpmy)
        fitaod = Fitaod(fitaodx, fitaody)


    fit = Fit(fitpm, fitaod)

    return fit