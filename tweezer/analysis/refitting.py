import os
from tweezer.io import read_tweebot_data_header
from tweezer.single.thermal_calibration import *
import numpy as np
import simplejson as json
from collections import OrderedDict as od


def get_immediate_subdirectories(dir):
    """Gets the subdirectories in the immediate lower level
        Args:
            dir (str): directory where to check for subdirectories
        Returns:
            list of subdirectories
        """

    return [name for name in os.listdir(dir) if os.path.isdir(os.path.join(dir, name))]


def get_data_files(dir):
    """Gets all the visible (not hidden) .txt files in the data folder of certain directory
    Args:
        dir (str): directory containing data folder with files
    Returns:
        list of not hidden data file names
    """

    return [name for name in os.listdir(dir+"/data/") if name[0]!="." and name[-4:]==".txt"]


def get_thermal_calibration_files(dir):
    """Gets all the visible (not hidden) .txt files in the "thermal_calibration" folder of certain directory
    Args:
        dir (str): directory containing "thermal_calibration" folder with files
    Returns:
        list of not hidden thermal_calibration file names
    """

    return [name for name in os.listdir(dir+"/thermal_calibration/") if name[0]!="." and name[-4:]==".txt"]


def new_values(pathData, pathThermalCalibration):
    """Calculates the new fitting values with MLE fitting and creates an ordered dictionary with new and old variables

    Args:
        pathData (str): path to the "data" file
        pathThermalCalibration (str): path to the "thermal_calibration" file
    Returns:
        hdict (OrderedDictionary): ordered dictionary containing the new and old variables of the fit
    """


    header = read_tweebot_data_header(pathData);

    new = {}
    newUnits = {}

    if 'fractionGlycerol' in header.metadata:
        new['fractionGlycerol'] = header.metadata['fractionGlycerol']
        new['fractionWater'] = header.metadata['fractionWater']
    else:
        new['fractionGlycerol'] = 0.1
        new['fractionWater'] = 0.9

    # set temperature to 25˚C and use the corresponding viscosity
    new['temperature'] = 25
    new['viscosity'] = 1e-6 * dynamic_viscosity_of_mixture(new["fractionWater"],
                                                           new["fractionGlycerol"],
                                                           new["temperature"])
    newUnits['viscosity'] = header.metadata['viscosity']
    newUnits['temperature'] = '˚C'

    # # get correct temperature and viscosity if possible, else use 27 ˚C
    # if header.metadata['viscosity'] is None:
    #     new['temperature'] = 27
    #     new['viscosity'] = 1e-6 * dynamic_viscosity_of_mixture(new["fractionWater"],
    #                                                            new["fractionGlycerol"],
    #                                                            new["temperature"])
    #     newUnits['viscosity'] = header.metadata['viscosity']
    #     newUnits['temperature'] = '˚C'
    # else:
    #     new['viscosity'] = header.metadata['viscosity']
    #     T = np.linspace(20, 35,1000)
    #     visc = [1e-6 * dynamic_viscosity_of_mixture(new['fractionWater'], new['fractionGlycerol'], t) for t in T]
    #     for indexV, v in enumerate(visc):
    #         if (v-new['viscosity'])/v<1e-3:
    #             new['temperature']=T[indexV]
    #             break
    #     newUnits['viscosity'] = header.metadata['viscosity']
    #     newUnits['temperature'] = '˚C'

    # do the fitting
    newFit = calibration_file(pathThermalCalibration, columns=[0,1,2,3], viscosity=new["viscosity"],
                              radii=[header.metadata["pmBeadRadius"],header.metadata["aodBeadRadius"]],
                              T=new["temperature"], plot=False)

    # create ordered dictionary
    hdict = od([
    ('general', od(
        [('date', header.metadata['date'].strftime('%Y-%m-%d %H:%M:%S')),
         ('duration', header.metadata['duration']),
         ('hasErrors', header.metadata['hasErrors']),
         ('errors', header.metadata['errors']),
         ('samplingRate', header.metadata['recordingRate']),
         ('acquisitionRate', header.metadata['samplingRate']),
         ('isAcquisitionAveraged', header.metadata['isDataAveraged']),
         ('nAcquisitionPerSample', header.metadata['nSamples']),
         ('isDataAveraged', 0),
         ('nSamplesPerPoint', 1),
         ('timeStep', header.metadata['timeStep']),
         ('startOfMeasurement_iteration', header.metadata['start of measurement (iteration) ']),
         ('endOfMeasurement_iteration', header.metadata['end of measurement (iteration) ']),
         ('laserDiodeHours', header.metadata['laserDiodeHours']),
         ('laserDiodeTemp', header.metadata['laserDiodeTemp']),
         ('laserDiodeCurrent', header.metadata['laserDiodeCurrent']),
         ('fractionGlycerol', new['fractionGlycerol']),
         ('fractionWater', new['fractionWater']),
         ('viscosity', new['viscosity']),
         ('temperature', new['temperature']),
         ('thermalCalibrationRefitted', True),
         ('units', od(
             [('duration', header.units['duration']),
              ('samplingRate', header.units['recordingRate']),
              ('acquisitionRate', header.units['samplingRate']),
              ('timeStep', header.units['timeStep']),
              ('startOfMeasurement_iteration', header.units['start of measurement (iteration) ']),
              ('endOfMeasurement_iteration', header.units['end of measurement (iteration) ']),
              ('laserDiodeHours', header.units['laserDiodeHours']),
              ('laserDiodeTemp', header.units['laserDiodeTemp']),
              ('laserDiodeCurrent', header.units['laserDiodeCurrent']),
              ('viscosity', header.units['viscosity']),
              ('temperature', newUnits['temperature'])
         ]))
    ])),
    ('aod', od(
      [('beadDiameter', header.metadata['aodBeadDiameter']),
       ('x', od(
            [('cornerFrequency', newFit.aod.x.fc),
             ('cornerFrequencyError', newFit.aod.x.sigma[1]),
             ('detectorOffset', header.metadata['aodDetectorOffsetX']),
             ('displacementSensitivity', newFit.aod.x.beta),
             ('displacementSensitivityError', newFit.aod.x.errorBeta),
             ('stiffness', newFit.aod.x.kappa),
             ('stiffnessError', newFit.aod.x.errorKappa)])),
       ('y', od(
            [('cornerFrequency', newFit.aod.y.fc),
             ('cornerFrequencyError', newFit.aod.y.sigma[1]),
             ('detectorOffset', header.metadata['aodDetectorOffsetY']),
             ('displacementSensitivity', newFit.aod.y.beta),
             ('displacementSensitivityError', newFit.aod.y.errorBeta),
             ('stiffness', newFit.aod.y.kappa),
             ('stiffnessError', newFit.aod.y.errorKappa)])),
        ('units', od(
            [('cornerFrequency', 'Hz'),
             ('detectorOffset', header.units['aodDetectorOffsetX']),
             ('displacementSensitivity', 'V / nm'),
             ('stiffness', 'pN / nm')
            ]))
    ])),
    ('pm', od(
      [('beadDiameter', header.metadata['pmBeadDiameter']),
       ('x', od(
            [('cornerFrequency', newFit.pm.x.fc),
             ('cornerFrequencyError', newFit.pm.x.sigma[1]),
             ('detectorOffset', header.metadata['pmDetectorOffsetX']),
             ('displacementSensitivity', newFit.pm.x.beta),
             ('displacementSensitivityError', newFit.pm.x.errorBeta),
             ('stiffness', newFit.pm.x.kappa),
             ('stiffnessError', newFit.pm.x.errorKappa)])),
       ('y', od(
            [('cornerFrequency', newFit.pm.y.fc),
             ('cornerFrequencyError', newFit.pm.y.sigma[1]),
             ('detectorOffset', header.metadata['pmDetectorOffsetY']),
             ('displacementSensitivity', newFit.pm.y.beta),
             ('displacementSensitivityError', newFit.pm.y.errorBeta),
             ('stiffness', newFit.pm.y.kappa),
             ('stiffnessError', newFit.pm.y.errorKappa)])),
        ('units', od(
            [('cornerFrequency', 'Hz'),
             ('detectorOffset', header.units['pmDetectorOffsetX']),
             ('displacementSensitivity', 'V / nm'),
             ('stiffness', 'pN / nm')
        ]))
    ])),
    ('oldValues', od(
        [('aod', od(
            [('x', od(
                [('displacementSensitivity', header.metadata['aodDisplacementSensitivityX']),
                 ('stiffness', header.metadata['aodStiffnessX'])
                ])),
             ('y', od(
                [('displacementSensitivity', header.metadata['aodDisplacementSensitivityY']),
                 ('stiffness', header.metadata['aodStiffnessY'])
                ])),
            ('units', od(
                [('displacementSensitivity', header.units['aodDisplacementSensitivityX']),
                 ('stiffness', header.units['aodStiffnessX'])
                ]))
           ])),
         ('pm', od(
            [('x', od(
                [('displacementSensitivity', header.metadata['pmDisplacementSensitivityX']),
                 ('stiffness', header.metadata['pmStiffnessX'])
                ])),
             ('y', od(
                [('displacementSensitivity', header.metadata['pmDisplacementSensitivityY']),
                 ('stiffness', header.metadata['pmStiffnessY'])
                ])),
            ('units', od(
                [('displacementSensitivity', header.units['pmDisplacementSensitivityX']),
                 ('stiffness', header.units['pmStiffnessX'])
                ]))
           ]))
        ]))
    ])
    return hdict


def change_format_only(pathData):

    """Creates an ordered dictionary with new format but old variables

    Args:
        pathData (str): path to the "data" file

    Returns:
        hdict (OrderedDictionary): ordered dictionary containing the new and old variables of the fit
    """

    header = read_tweebot_data_header(pathData);
    new = {}
    newUnits = {}
    # do we really want to set this for the oldValues array if it was not set before?
    if 'fractionGlycerol' in header.metadata:
        new['fractionGlycerol'] = header.metadata['fractionGlycerol']
        new['fractionWater'] = header.metadata['fractionWater']
    else:
        new['fractionGlycerol'] = 0.1
        new['fractionWater'] = 0.9

    # set temperature to 25˚C and use the corresponding viscosity
    new['temperature'] = 25
    new['viscosity'] = 1e-6 * dynamic_viscosity_of_mixture(new["fractionWater"],
                                                           new["fractionGlycerol"],
                                                           new["temperature"])
    newUnits['viscosity'] = header.metadata['viscosity']
    newUnits['temperature'] = '˚C'

    # # set viscosity and temperature
    # if header.metadata['viscosity'] is None:
    #     new['temperature'] = 27
    #     new['viscosity'] = 1e-6 * dynamic_viscosity_of_mixture(new["fractionWater"],
    #                                                            new["fractionGlycerol"],
    #                                                            new["temperature"])
    #     newUnits['viscosity'] = header.metadata['viscosity']
    #     newUnits['temperature'] = '˚C'
    # else:
    #     new['viscosity'] = header.metadata['viscosity']
    #     T = np.linspace(20, 35,1000)
    #     visc = [1e-6 * dynamic_viscosity_of_mixture(new['fractionWater'], new['fractionGlycerol'], t) for t in T]
    #     for indexV, v in enumerate(visc):
    #         if (v-new['viscosity'])/v<1e-3:
    #             new['temperature']=T[indexV]
    #             break
    #     newUnits['viscosity'] = header.metadata['viscosity']
    #     newUnits['temperature'] = '˚C'

    hdict = od([
    ('general', od(
        [('date', header.metadata['date'].strftime('%Y-%m-%d %H:%M:%S')),
         ('duration', header.metadata['duration']),
         ('hasErrors', header.metadata['hasErrors']),
         ('errors', header.metadata['errors']),
         ('samplingRate', header.metadata['recordingRate']),
         ('acquisitionRate', header.metadata['samplingRate']),
         ('isAcquisitionAveraged', header.metadata['isDataAveraged']),
         ('nAcquisitionPerSample', header.metadata['nSamples']),
         ('isDataAveraged', 0),
         ('nSamplesPerPoint', 1),
         ('timeStep', header.metadata['timeStep']),
         ('startOfMeasurement_iteration', header.metadata['start of measurement (iteration) ']),
         ('endOfMeasurement_iteration', header.metadata['end of measurement (iteration) ']),
         ('laserDiodeHours', header.metadata['laserDiodeHours']),
         ('laserDiodeTemp', header.metadata['laserDiodeTemp']),
         ('laserDiodeCurrent', header.metadata['laserDiodeCurrent']),
         ('fractionGlycerol', new['fractionGlycerol']),
         ('fractionWater', new['fractionWater']),
         ('viscosity', new['viscosity']),
         ('temperature', new['temperature']),
         ('thermalCalibrationRefitted', False),
         ('units', od(
             [('duration', header.units['duration']),
              ('samplingRate', header.units['recordingRate']),
              ('acquisitionRate', header.units['samplingRate']),
              ('timeStep', header.units['timeStep']),
              ('startOfMeasurement_iteration', header.units['start of measurement (iteration) ']),
              ('endOfMeasurement_iteration', header.units['end of measurement (iteration) ']),
              ('laserDiodeHours', header.units['laserDiodeHours']),
              ('laserDiodeTemp', header.units['laserDiodeTemp']),
              ('laserDiodeCurrent', header.units['laserDiodeCurrent']),
              ('viscosity', header.units['viscosity']),
              ('temperature', newUnits['temperature'])
         ]))
    ])),
    ('aod', od(
      [('beadDiameter', header.metadata['aodBeadDiameter']),
        ('x', od(
            [('displacementSensitivity', header.metadata['aodDisplacementSensitivityX']),
             ('stiffness', header.metadata['aodStiffnessX']),
             ('detectorOffset', header.metadata['aodDetectorOffsetX']),
            ])),
        ('y', od(
            [('displacementSensitivity', header.metadata['aodDisplacementSensitivityY']),
             ('stiffness', header.metadata['aodStiffnessY']),
             ('detectorOffset', header.metadata['aodDetectorOffsetY']),
            ])),
        ('units', od(
            [('displacementSensitivity', header.units['aodDisplacementSensitivityX']),
             ('stiffness', header.units['aodStiffnessX']),
             ('detectorOffset', header.units['aodDetectorOffsetX']),
            ]))
    ])),
    ('pm', od(
      [('beadDiameter', header.metadata['pmBeadDiameter']),
       ('x', od(
                [('displacementSensitivity', header.metadata['pmDisplacementSensitivityX']),
                 ('stiffness', header.metadata['pmStiffnessX']),
                 ('detectorOffset', header.metadata['pmDetectorOffsetX']),
                ])),
             ('y', od(
                [('displacementSensitivity', header.metadata['pmDisplacementSensitivityY']),
                 ('stiffness', header.metadata['pmStiffnessY']),
                 ('detectorOffset', header.metadata['pmDetectorOffsetY']),
                ])),
            ('units', od(
                [('displacementSensitivity', header.units['pmDisplacementSensitivityX']),
                 ('stiffness', header.units['pmStiffnessX']),
                 ('detectorOffset', header.units['pmDetectorOffsetX']),
                ]))
    ])),

    ])
    return hdict


def refit_files(directory):
    """Rewrites the files of one directory with the new header in json format

    Args:
        directory (str): path of the directory containing data and thermal_calibration folders
    """

    fileNames = get_data_files(directory)
    for file in fileNames:
        # display current state
        print('Processing: ' + file + ' in ' + directory)
        # check for corresponding thermal calibration file
        tsFiles = get_thermal_calibration_files(directory)
        tsFile = 'TS_' + file
        otherTsFile = 'TS_' + file.split('_', maxsplit=1)[0] + '.txt'
        foundTsFile = False
        if tsFile in tsFiles:
            foundTsFile = True
        elif otherTsFile in tsFiles:
            foundTsFile = True
            tsFile = otherTsFile

        # check if the new file is already a json file
        fOld = open(directory+"/data/"+file, "r")
        line = fOld.readline().strip()
        fOld.close()
        if line[0] == '{':
            print('    Skipping file as it already has a json header.')
            continue

        if foundTsFile:
            newHeader = new_values(directory+"/data/"+file, directory+"/thermal_calibration/" + tsFile)
        else:
            newHeader = change_format_only(directory+"/data/"+file)
            print("The file", directory+"/"+file, "does not have a thermal calibration file. Old calibration values remain.")

        fOld = open(directory+"/data/"+file, "r")
        line = fOld.readline()
        while line[0] == "#" or line.strip() == "":
                line = fOld.readline()
        data = fOld.read()
        fOld.close()

        fNew = open(directory+"/data/"+file, "w")
        fNew.write(json.dumps(newHeader, indent=4))
        fNew.write("\n\n#### DATA ####\n\n")
        fNew.write(line)
        fNew.write(data)
        fNew.close()


def refit_directories(directory):
    """Goes through subdirectories looking for folders containing "data" and "thermal_calibration" folders

    Args:
        directory (str): path of the directory containing data and thermal_calibration folders
    """

    # check last character in path
    if directory[-1] != '/':
        directory += '/'

    subDirectories = get_immediate_subdirectories(directory)
    if 'data' and 'thermal_calibration' in subDirectories:
        refit_files(directory)
    else:
        for subdir in subDirectories:
            refit_directories(directory + subdir+"/")
