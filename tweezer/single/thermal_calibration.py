import os
import glob
import math
import numpy as np
from scipy.optimize import curve_fit

import matplotlib.pyplot as plt



#Parameters:
radius = 1000             #nm
viscosity = 3.3e-9        #pN/nm^2s
kb = 1.3806488e-23        #IS
T = 300                   #K
drag_coef = 6*math.pi*radius*viscosity


block = 8192              #number of data points per block
samplingRate = 80000     #sampling rate of data acquisition
overlap = 0             #overlap between the blocks for the calculation of the PSD function



filesPath=os.path.dirname(os.path.realpath(__file__))


def lorentz_fit(f,D,fc):
    """
    Lorentzian function to fit the PSD function

    Parameters
    ----------
    f : np.array
        frequency in units of [Hz]

    D : float
        diffusion constant in units of [V]

    fc : float
        corner frequency in units of [Hz]

    Returns
    -------
    PSD values : np.array
        returns the function in order to perform the fit
    """

    return D/((math.pi)**2*(f**2+fc**2))


def get_files(filesPath=os.path.dirname(os.path.realpath(__file__)), pattern='TS*.txt'):
    """
    List with the files to be calibrated

    Parameters
    ----------
    filesPath : str
        Path to the folder with files
        Default : path of the script

    Returns
    -------
    files : list
        contains all the files matching the requirements
    """

    files=[]
    os.chdir(filesPath)
    for file in glob.glob(pattern):
            files.append(file)
    files.sort()
    return files


def read_files(file,header=7):
    """
    Reads a .txt file to obtain the data

    Parameters
    ----------
    file : str
        name of the file containing the data

    header : int
        number of lines comprising the header (including variable name of columns)
        Default : 7 (according to thermal calibration data files from 2014)

    Returns
    -------
    data : np.array
    """
    data=np.loadtxt(file,delimiter="\t",usecols=(0, 1, 2, 3),skiprows=header,unpack=True)
    return data


def distance_calibration(D):
    """Distance calibration factor (beta) in units of [V/nm]

    Parameters
    ----------
    D : float
        diffusion constant in units of [V]

    Returns
    -------
    beta : float
        distance calibration factor in units of [V/nm]
    """

    beta=1/math.sqrt(kb*T*1e21/(drag_coef*D))

    return beta


def trap_stiffness(fc):
    """Trap stiffness in units of [pN/nm]

    Parameters
    ----------
    fc : float
        corner frequency in units of [Hz]

    Returns
    -------
    kappa : float
        trap stiffness in units of [pN/nm]
    """

    kappa=2*math.pi*fc*drag_coef

    return kappa


def force_calibration(beta,kappa):
    """force calibration factor in units of [pN/V]

    Parameters
    ----------
    beta : float
        distance calibration factor in units of [V/nm]

    kappa : float
        trap stiffness in units of [pN/nm]

    Returns
    -------
    alpha : float
        force calibration factor in units of [pN/V]
    """

    alpha=kappa/beta

    return alpha


def fitting(psd,f,limit=None):
    """Fits the power spectrum distribution function to the lorentz_fit curve. Limit refers to
    the maximum frequency considered for the fit

    Parameters
    ----------
    psd : list
        Power spectrum distribution values from the function matplotlib.psd in units of [Hz^-1]

    f : list
        Frequency in units of (Hz)

    limit : float
        maximum frequency to perform the fitting
        Default: None

    Returns
    -------

        results : list
            Parameters of the fitting --> result[0]=D [V], result[1]=fc [Hz]

        error: list
            Contains the variances (errors of the parameters in the diagonal)
    """

    result, error = curve_fit(lorentz_fit, f[2:len(psd)*limit], psd[2:len(psd)*limit])

    return result, error


def show_fit(psd, f, result):
    """
    Plots the PSD and the fit

    Parameters
    ----------
    psd : list of float
        PSD values

    f : list of float
        Frequency values

    result : list of float
        Parameters obtained from the Lorentzian fit
    """

    y = lorentz_fit(f, result[0], result[1])

    plt.plot(f[2:], psd[2:])
    plt.plot(f[2:len(psd)*0.5], y[2:len(psd)*0.5])
    plt.yscale('log')
    plt.xscale('log')
    plt.show()


def factors_from_data(data, limit=0.5, plot=False):
    """Calculates the Power Spectrum Density function of data, fits it to a Lorentzian and
    returns the distance calibration factor [V/pN], the trap stiffness [pN/nm] and
    the force calibration factor [pN/V]

    Parameters
    ----------
    data : np.array
        Data from the time series file

    limit : float
        Sets the maximum frequency to be considered in the fit
        Default: 0.5 (to remove the tail)

    plot : bool
        When True, it plots the PSD and the fit
        Default: False

    Returns
    -------
    beta, kappa, alpha : float
        Distance calibration factor [V/nm], trap stiffness [pN/nm] and force calibration factor [pN/V]
    """

    psd, f = plt.psd(data, NFFT=block, Fs=samplingRate, noverlap=overlap, scale_by_freq=True)
    result, error = fitting(psd, f, limit)

    if plot == True:
        show_fit(psd, f, result)

    beta = distance_calibration(result[0])
    kappa = trap_stiffness(result[1])
    alpha = force_calibration(beta, kappa)

    return beta, kappa, alpha


def calibrate_file(file, limit=0.5, plot=False):
    """
    Obtain the distance calibration factor [V/nm], the trap stiffness [pN/nm] and the force calibration factor [pN/V]
    values for a file after fitting the PSD function

    Parameters
    ----------
    file : str
        Path to the file containing the time series data

    limit : float
        Sets the maximum frequency to be considered in the fit
        Default: 0.5 (to remove the tail)

    plot : bool
        When True, it plots the PSD and the fit
        Default: False

    Returns
    -------
    betaV, kappaV, alphaV : lists of lists of float
        beta, kappa and alpha values (respectively) of each trap and component (T1X, T1Y, T2X, T2Y)
    """

    #Lists with the beta, kappa and alpha values from each file
    betaV = []
    kappaV = []
    alphaV = []

    data = read_files(file)

    for column in data:

        beta, kappa, alpha = factors_from_data(column, limit, plot)
        betaV.append(beta)
        kappaV.append(kappa)
        alphaV.append(alpha)

    print(betaV, kappaV, alphaV)
    return betaV, kappaV, alphaV


def calibrate_directory(directory=os.path.dirname(os.path.realpath(__file__)), pattern='TS*.txt', limit=0.5, plot=False):
    """
    Obtain the beta, kappa and alpha values for TS files in a directory after fitting the psd

    Parameters
    ----------
    directory : str
        Path to the directory with the files (excluding the file)
        Default: directory where the script is running
    pattern : str
        Defines the filter to open the files of the directory
        Default: all time series .txt files of the directory

    limit : float
        Sets the maximum frequency to be considered in the fit
        Default: 0.5 (to remove the tail)

    plot : bool
        When True, it plots the PSD and the fit
        Default: False

    Returns
    -------
    betaV, kappaV, alphaV : lists of float
        beta, kappa and alpha values (respectively) of each trap and component, and of each file
        Format: [[file1_T1X, file1_T1Y, file1_T2X, file1_T2Y],
        ..., [fileN_T1X, fileN_T1Y, fileN_T2X, fileN_T2Y]]
    """

    #Lists with the beta, kappa and alpha values from each file
    betaV = []
    kappaV = []
    alphaV = []

    files = get_files(directory, pattern)
    print(files)

    for file in files:

        beta, kappa, alpha = calibrate_file(directory+'/'+file, limit, plot)

        betaV.append(beta)
        kappaV.append(kappa)
        alphaV.append(alpha)

    print(betaV, kappaV, alphaV)
    return betaV, kappaV, alphaV


#TODO: check the optimal limit value

