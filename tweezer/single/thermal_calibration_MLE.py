# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import os
import glob
import math
import numpy as np

from operator import itemgetter
import scipy.optimize as op
from scipy.optimize import curve_fit
from scipy.signal import welch

import matplotlib.pyplot as plt



#Parameters:
_radius = 1000             #nm
viscosity = 1.2198e-9        #pN/nm^2s
kb = 1.3806488e-23        #IS
T = 300                   #K
rho=1000e-27
rhobead=1050e-27
mass=rhobead*4/3*math.pi*_radius**3

drag_coef = 6*math.pi*_radius*viscosity
fv=1e-3*(viscosity/rho)/(math.pi * (_radius)**2)
fm= 1e-3*drag_coef/(2*math.pi*(mass+2*math.pi*rho*(_radius)**3/3))


block = 4096              #number of data points per block
samplingRate = 80000     #sampling rate of data acquisition
overlap = 0             #overlap between the blocks for the calculation of the PSD function


pathFile='/home/avellaneda/Escritorio/Portatil Mario 24-09-12/DATOS/Mario/BIOTEC/Thesis/Thermal calibration/TS_8.txt'


def read_files(file=pathFile,header=7):
    """
    Reads a .txt file to obtain the data. It gets the columns specified in usecols and ignors the lines
    specified by header.

    Args:
        file (str): name of the file containing the data
        header (int): number of lines comprising the header (including variable name of columns)
            Default : 7 (according to thermal calibration data files from 2014)

    Returns:
        data (np.array): returns the columns specified in usecols
    """
    data=np.loadtxt(file,delimiter="\t",usecols=(0, 1, 2, 3 ),skiprows=header,unpack=True)
    return data


def lorentz_fit(f,D,fc):
    """
    Lorentzian function to fit the PSD function

    Args:
        f (np.array): frequency in units of [Hz]
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]

    Returns:
        Lorentzian values(np.array): Lorentzian function with the corresponding parameters
    """

    return D/((math.pi)**2*(f**2+fc**2))


def distance_calibration(D):
    """Distance calibration factor (beta) in units of [V/nm]

    Args:
        D (float): diffusion constant in units of [V]

    Returns:
        beta (float): distance calibration factor in units of [V/nm]
    """

    beta=1/math.sqrt(kb*T*1e21/(drag_coef*D))

    return beta


def trap_stiffness(fc):
    """Trap stiffness in units of [pN/nm]

    Args:
        fc (float): corner frequency in units of [Hz]

    Returns:
        kappa (float): trap stiffness in units of [pN/nm]
    """

    kappa=2*math.pi*fc*drag_coef

    return kappa


def force_calibration(beta, kappa):
    """force calibration factor in units of [pN/V]

    Args:
        beta (float): distance calibration factor in units of [V/nm]
        kappa (float): trap stiffness in units of [pN/nm]

    Returns:
        alpha (float): force calibration factor in units of [pN/V]
    """

    alpha=kappa/beta

    return alpha

def mle_factors(x,y):
    """
    Calculation of the S coefficients related to the MLE, according to the paper of Norrelike
    
    Args:
        x (np.array): Frequency in [Hz]
        y (np.array): Experimental PSD function in [V^2]
    
    Returns:
        s (list of float): matrix with the S coefficients
    """
    s01=1/(len(x)) * np.sum(y)
    s02=1/(len(x)) * np.sum(np.power(y,2))
    s11=1/(len(x)) * np.sum(np.multiply(np.power(x,2), y))
    s12=1/(len(x)) * np.sum(np.multiply(np.power(x,2), np.power(y,2)))
    s22=1/(len(x)) * np.sum(np.multiply(np.power(x,4), np.power(y, 2)))
    s=[[0, s01, s02], [0, s11, s12], [0, s12, s22]]
 
    return s

def mle_ab(s):
    """
    Calculation of the pre-parameters a and b, according to the paper of Norrelike
    
    Args:
        s (list of float): matrix with the S coefficients
    
    Returns:
        a, b (float): pre-parameters for the calculation of D and fc
    """
    
    a = 1/(s[0][2]*s[2][2]-s[1][2]*s[1][2])*(s[0][1]*s[2][2]-s[1][1]*s[1][2])
    b = 1/(s[0][2]*s[2][2]-s[1][2]*s[1][2])*(s[1][1]*s[0][2]-s[0][1]*s[1][2])
    return a, b

def mle_parameters(a, b, n):
    """Calculate parameters from the factors of the MLE
    
    Args:
        a, b (float): pre-parameters for the calculation of D and fc
        n: number of frequency data points
    
    Returns:
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]
    
    """
    
    if a*b>0:
        fc = math.sqrt(a/b)
    else:
        fc = 0
    D = (math.pi)**2 / b

    return D, fc


def mle_errors(x, D, fc, a, b, n):
    """Function to get the standard deviation of the parameters according to the paper of Norrelyke
    
    Args:
        x (np.array): array of the frequencies in units of [Hz]
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]
        a, b (float): pre-parameters for the calculation of D and fc    
        n: number of frequency data points

    Returns:
        errosMle (np.array): with sigma(D) and sigma(fc)
    """
    y = lorentz_fit(x,D,fc)
    s=mle_factors(x,y)
    sB = [[s[0][2], s[1][2]], [s[1][2], s[2][2]]]
    sError = 1/(128*n)*np.linalg.inv(sB)
    
    sigmaFc = fc**2/4 * (sError[0][0]/a**2+sError[1][1]/b**2-2*sError[0][1]/(a*b))
    sigmaD = D**2*(sError[1][1]/b**2)
    errorsMle = [np.sqrt(sigmaD), np.sqrt(sigmaFc)]

    return errorsMle


def residuals(f, psdExp, D, fc):
    """Calculates the average of the residuals squared to test the best fitting limits
    
    Args:
        f (np.array): array of the frequencies in units of [Hz]
        psdExp (np.array): array of the experimental values of the PSD in units of [V^2]
        D (float): diffusion constant in units of [V]
        fc (float): corner frequency in units of [Hz]
    Returns:
        np.mean(res) (float): the mean of the residuals squared
    """
    
    psdTheo = lorentz_fit(f, D, fc)
    res = [(exp-theo)**2 for exp, theo in zip(psdExp, psdTheo)]
    
    return np.mean(res)


def factors_from_data(data, limit, plot=False):
    """Calculates the Power Spectrum Density function of data, fits it with Maximum Likelyhood Method (according to 
    the reference given), and calculates the Diffusion constant [V] and the corner frequency [Hz]

    Args:
        data (np.array): data from the time series file
        limit (float): sets the maximum frequency to be considered in the fit
        plot (bool): when True, it plots the PSD and the fit (Default: False)

    Returns:
        D (float): diffusion constant in units of V
        fc (float): corner frequency in units of Hz
        errors (list of float): standard deviation of the parameters
        check (float): average of the squared residues

    """

    fRead, psdRead = welch(data, nperseg=block, fs=samplingRate, noverlap=overlap)

    f = fRead[2:len(fRead)*limit]
    psd = psdRead[2:len(psdRead)*limit]


    S = mle_factors(f, psd)
    a, b = mle_ab(S)
    D, fc = mle_parameters(a, b, len(f))
    result = [D, fc]
    
    errors = mle_errors(f, result[0], result[1], a, b, len(f))   

    check = residuals(f,psd,result[0], result[1])

    y=[lorentz_fit(x, D, fc) for x in f]
    if plot == True:

        plt.plot(fRead[2:], psdRead[2:], color='green')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('PSD (V^2)')

        plt.plot(f, y, color='orange', label = 'Maximum likelihood by S factors')

        plt.yscale('log')
        plt.xscale('log')
        plt.show()


    return D, fc, errors, check


def calibrate_file(data, limit=0.05, plot=False):
    """
    Obtain the distance calibration factor [V/nm], the trap stiffness [pN/nm] and the force calibration factor [pN/V]
    values for a file after fitting the PSD function

    Args:
        data (np.array): data from the time series file
        limit (float): sets the maximum frequency to be considered in the fit
        plot (bool): when True, it plots the PSD and the fit (Default: False)

    Returns:
        DV (list of float): array with the values of the diffusion constant in units of [V] for all columns
        fcV (list of float): array with the values of the corner frequency in units of [Hz] for all columns
        errorV (list of float): array with the values of the standard deviations for all columns
        checkV  (list of float): array with the values of the mean of residuals squared for all columns
    """

    #Lists with the beta, kappa and alpha values from each file
    DV = []
    fcV = []
    checkV = []
    errorV = []

    for column in data:
        #print(len(column))
        D, fc, sigma, check = factors_from_data(column, limit, plot)
        DV.append(D)
        fcV.append(fc)
        errorV.append(sigma)
        checkV.append(check)

    #print(betaV, kappaV, alphaV)
    return DV, fcV, errorV, checkV


def iterative_fitting(file, plot=False):
    """Performs the fitting with different limits and chooses the 
    one with least deviation (minimum mean residuals squared)
    
    Args:
        data (np.array): data read from the file
        plt (bool): if True, the fittings are plotted. Default: False
        
    Returns:
        D (list of float): diffusion coefficients in units of [v]
        fc (list of float): corner frequancies in units fo [Hz]
        errors (list of lists of float): standard deviations of the parameters
    
    """

    data = read_files(file)

    limitList = [0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.12, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]
    limitList2 = [.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
    
    Ds = []
    fcs = []
    checks = []
    sigmas = []
    
    for l in limitList:
        DV, fcV, sigmaV, checkV = calibrate_file(data, limit=l, plot=False)
        Ds.append(DV)
        fcs.append(fcV)
        sigmas.append(sigmaV)
        checks.append(checkV)
    
    
    DPMX = [D[0] for D in Ds]  
    DPMY = [D[1] for D in Ds]
    DAODX = [D[2] for D in Ds]
    DAODY = [D[3] for D in Ds]
    
    fcPMX = [fc[0] for fc in fcs]  
    fcPMY = [fc[1] for fc in fcs]  
    fcAODX = [fc[2] for fc in fcs]  
    fcAODY = [fc[3] for fc in fcs]  
    
    sigmaPMX = [s[0] for s in sigmas]  
    sigmaPMY = [s[1] for s in sigmas]  
    sigmaAODX = [s[2] for s in sigmas]  
    sigmaAODY = [s[3] for s in sigmas] 
    
    checksPMX = [c[0] for c in checks]
    checksPMY = [c[1] for c in checks]
    checksAODX = [c[2] for c in checks]
    checksAODY = [c[3] for c in checks]
    
    
    optPMX = min(enumerate(checksPMX), key=itemgetter(1))[0]
    optPMY = min(enumerate(checksPMY), key=itemgetter(1))[0]
    optAODX = min(enumerate(checksAODX), key=itemgetter(1))[0]
    optAODY = min(enumerate(checksAODY), key=itemgetter(1))[0]
    
    
    print(DPMX[optPMX], fcPMX[optPMX], sigmaPMX[optPMX])
    print(DPMY[optPMY], fcPMY[optPMY], sigmaPMY[optPMY])
    print(DAODX[optAODX], fcAODX[optAODX], sigmaAODX[optAODX])
    print(DAODY[optAODY], fcAODY[optAODY], sigmaAODY[optAODY])
        
    
    print(optPMX)
    print(optPMY)
    print(optAODX)
    print(optAODY)
        
    if plot==True:
        factors_from_data(data[0],limit=limitList[optPMX],plot=True)
        factors_from_data(data[1],limit=limitList[optPMY],plot=True)
        factors_from_data(data[2],limit=limitList[optAODX],plot=True)
        factors_from_data(data[3],limit=limitList[optAODY],plot=True)
        
    D = [DPMX[optPMX], DPMY[optPMY], DAODX[optAODX], DAODY[optAODY]]
    fc = [fcPMX[optPMX], fcPMY[optPMY], fcAODX[optAODX], fcAODY[optAODY]]
    errors = [sigmaPMX[optPMX], sigmaPMY[optPMY], sigmaAODX[optAODX], sigmaAODY[optAODY]]
    
    return D, fc, errors
    #plt.plot(limitList2,checksPMX, 'o')
    #plt.show()
    

D, fc, errors = iterative_fitting(data, plot=True)

#Calculation of the used parameters:

beta = [distance_calibration(diff) for diff in D]
kappa = [trap_stiffness(freq) for freq in fc]
alpha = [force_calibration(be, ka) for be, ka in zip(beta,kappa)]

print(beta)
print(kappa)
print(alpha)




