import os
import glob
import math
import numpy as np
import scipy.optimize as op
from scipy.optimize import curve_fit
from scipy.signal import welch

import matplotlib.pyplot as plt



#Parameters:
radius = 1000             #nm
viscosity = 1.2198e-9        #pN/nm^2s
kb = 1.3806488e-23        #IS
T = 300                   #K
rho=1000e-27
rhobead=1050e-27
mass=rhobead*4/3*math.pi*radius**3

drag_coef = 6*math.pi*radius*viscosity
fv=1e-3*(viscosity/rho)/(math.pi * (radius)**2)
fm= 1e-3*drag_coef/(2*math.pi*(mass+2*math.pi*rho*(radius)**3/3))


block = 4096              #number of data points per block
samplingRate = 80000     #sampling rate of data acquisition
overlap = 400             #overlap between the blocks for the calculation of the PSD function



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

def lorentz_hyd_fit(f,D,fc):
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

    return D*(1+np.sqrt(f/fv))/((fc-f**(3/2)/fv**(1/2)-f**2/fm)**2+(f+f**(3/2)/fv**(1/2))**2)


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


def fitting(psd, f, limit=None,  w=None, result=[0.001,0.02]):
    """Fits the power spectrum distribution function to the lorentz_hyd_fit curve. Limit refers to
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

    result, error = curve_fit(lorentz_hyd_fit, f, psd, p0=[result[0], result[1]], sigma=w)
    print(result)
    return result, error



def show_fit_hyd(psd, f, result, limit):
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

    y = lorentz_hyd_fit(f, result[0], result[1])

    plt.plot(f[2:], psd[2:])
    plt.plot(f[2:len(psd)*limit], y[2:len(psd)*limit])
    plt.yscale('log')
    plt.xscale('log')

def show_fit(psd, f, result, limit):
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
    plt.plot(f[2:len(psd)*limit], y[2:len(psd)*limit])
    plt.yscale('log')
    plt.xscale('log')

def mle(x, y, result):

    """Function to optimize the maximum likelihood.

    Source of the formula for the ML: Norrelike"""


    def lnlike(theta, x, y):
        D, fc = theta
        model = D / ((math.pi**2) * (fc**2 + x**2))
        return np.sum(np.add(np.divide(y, model), np.log(model)))


    nll = lambda *args: lnlike(*args)
    result = op.minimize(nll, [result[0], result[1]], args=(x, y))

    D_ml, fc_ml = result["x"]
    return D_ml, fc_ml


def mle_factors(x,y):
    """Second method of MLE, calculating the factors according to the paper of Norrelike
    """
    s01=1/(len(x)) * np.sum(y)
    s02=1/(len(x)) * np.sum(np.power(y,2))
    s11=1/(len(x)) * np.sum(np.multiply(np.power(x,2), y))
    s12=1/(len(x)) * np.sum(np.multiply(np.power(x,2), np.power(y,2)))
    s22=1/(len(x)) * np.sum(np.multiply(np.power(x,4), np.power(y, 2)))
    s=[[0, s01, s02], [0, s11, s12], [0, s12, s22]]
    print(s[0][0],s[0][1],s[0][2],s[1][0],s[1][1],s[1][2],s[2][0],s[2][1],s[2][2])
    return s

def calculate_parameters(s, n):
    """Calculate parameters from the factors of the MLE"""
    fc = math.sqrt((s[0][1]*s[2][2]-s[1][1]*s[1][2])/(s[1][1]*s[0][2]-s[0][1]*s[1][2]))
    D = (math.pi)**2 * (s[0][2]*s[2][2]-s[1][2]*s[1][2])/(s[1][1]*s[0][2]-s[0][1]*s[1][2])

    return D, fc


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

    fRead, psdRead = welch(data, nperseg=block, fs=samplingRate, noverlap=overlap)

    f = fRead[2:len(fRead)*limit]
    psd = psdRead[2:len(psdRead)*limit]

    resultHyd, errorHyd = curve_fit(lorentz_hyd_fit, f, psd)

    if resultHyd[1] < 0:
        resultHyd[1] = -resultHyd[1]

    result, error = curve_fit(lorentz_fit, f, psd, p0=[resultHyd[0], resultHyd[1]])

    if result[1] < 0:
        result[1] = -result[1]


    resultMle = mle(f, psd, result)



    coeff=mle_factors(f[2:len(psd)*limit],psd[2:len(psd)*limit])

    resultMleFactors = calculate_parameters(coeff, len(f))
    a,b=resultMleFactors
    resultMleFac=[a,b]
    print(result)



    print(resultHyd[0], result[0], resultMle[0], resultMleFac[0])
    print(resultHyd[1], result[1], resultMle[1], resultMleFac[1])

    y = lorentz_fit(f, result[0], result[1])
    yHyd = lorentz_hyd_fit(f, resultHyd[0], resultHyd[1])
    yMle = lorentz_fit(f, resultMle[0], resultMle[1])
    yMleFac = lorentz_fit(f, resultMleFac[0], resultMleFac[1])

    residualsLorentz = [(exp-theo) for exp, theo in zip(psd, y)]
    residualsHyd = [(exp-theo) for exp, theo in zip(psd, yHyd)]
    residualsMle = [(exp-theo) for exp, theo in zip(psd, yMle)]
    """
    plt.figure(2)
    plt.subplot(311)
    plt.plot(f,residualsLorentz, 'o')

    plt.subplot(312)
    plt.plot(f,residualsHyd, 'o')

    plt.subplot(313)
    plt.plot(f, residualsMle, 'o')
    plt.show()
    """
    if plot == True:

        plt.plot(fRead[2:], psdRead[2:], color='green')
        plt.plot(f, y, color='red', label='Lorentzian')
        plt.plot(f, yHyd, color='blue', label = 'Hydrodynamic corrections')
        plt.plot(f, yMle, color='black', label = 'Maximum likelihood')
        plt.plot(f, yMleFac, color='green', label = 'Maximum likelihood by S factors')
        plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
        plt.yscale('log')
        plt.xscale('log')
        plt.show()



    beta = distance_calibration(result[0])
    kappa = trap_stiffness(result[1])
    alpha = force_calibration(beta, kappa)

    return beta, kappa, alpha


def calibrate_file(file, limit=0.05, plot=False):
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
        #print(len(column))
        beta, kappa, alpha = factors_from_data(column, limit, plot)
        betaV.append(beta)
        kappaV.append(kappa)
        alphaV.append(alpha)

    #print(betaV, kappaV, alphaV)
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


calibrate_file('/home/avellaneda/Escritorio/Portatil Mario 24-09-12/DATOS/'
               'Mario/BIOTEC/Thesis/Thermal calibration/old data/TS_7.txt', limit=0.2, plot=True)


#TODO: check the optimal limit value

