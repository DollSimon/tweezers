from collections import OrderedDict
from distutils.util import strtobool
from pathlib import Path


def get_files(path, suffix=None, prefix=None, parent=None, recursive=False, hiddenFiles=False):
    """
    Recursively get all files in the given path. If suffix, prefix or parent are set, only files
    meeting these conditions are returned.

    Args:
        path (pathlib.Path or str): path to the directory to check recursively
        suffix (str): filter by file suffix (default: None)
        prefix (str): filter by file prefix (default: None)
        parent (str): filter by parent directory name (default: None)
        recursive (bool):
        hiddenFiles (bool):

    Returns:
        list of `pathlib.Path`
    """

    if type(path) is str:
        path = Path(path)

    # store result
    res = []

    # check each element in the current directory
    for element in path.iterdir():
        if element.is_dir() and recursive:
            # recursively call the function on subdirectories
            get_files(element, suffix=suffix, prefix=prefix, parent=parent, hiddenFiles=hiddenFiles)
        else:
            # store the element
            candidate = element
            # check all conditions and reset candidate if one of them
            if suffix is not None and element.suffix != suffix:
                candidate = None
            elif parent is not None and element.parts[-2] != parent:
                candidate = None
            elif prefix is not None and not element.parts[-1].startswith(prefix):
                candidate = None
            elif not hiddenFiles and element.parts[-1].startswith('.'):
                candidate = None

            if candidate:
                res.append(candidate)

    return res


def meta_insert_from_key(meta, key, value):
    """
    Insert a key into the metadata nested OrderedDictionary structure. The key position is given as a list of
    sub-keys. The nested dictionaries are created when necessary.

    Usage:

        >>> meta = OrderedDict()
        >>> key = ['aod', 'stiffness', 'x']
        >>> value = 1
        >>> meta_insert_from_key(meta, key, value)
        >>>
        >>> print(meta)
        >>> OrderedDict([('aod', OrderedDict([('stiffness', OrderedDict([('x', 1)]))]))])

    Args:
        meta (OrderedDictionary): metadata structure of nested OrderedDictionaries
        key (list): list of strings that are the keys that lead to the element in the metadata structure
        value: key's value
    """

    if len(key) == 1:
        meta[key[0]] = value
    else:
        if key[0] not in meta:
            meta[key[0]] = OrderedDict()
        meta_insert_from_key(meta[key[0]], key[1:], value)


def get_meta_key(key):
    """
    Get the "key-path" in the nested metadata dictionary for an header key.

    Args:
        key (string): the header key to look up

    Returns:
        list of strings
    """

    key_mapper = {
        'laserDiodeTemp': ['laser', 'diodeTemp'],
        'laserDiodeTempUnit': ['laser', 'diodeTempUnit'],
        'laserDiodeHours': ['laser', 'diodeHours'],
        'laserDiodeHoursUnit': ['laser', 'diodeHoursUnit'],
        'laserDiodeCurrent': ['laser', 'diodeCurrent'],
        'laserDiodeCurrentUnit': ['laser', 'diodeCurrentUnit'],

        # aod variables
        'aodCornerFreqX': ['aod', 'cornerFreq', 'x'],
        'aodCornerFreqY': ['aod', 'cornerFreq', 'y'],
        'aodCornerFreqXUnit': ['aod', 'cornerFreq', 'unit'],
        'aodCornerFreqYUnit': ['aod', 'cornerFreq', 'unit'],

        'aodDetectorOffsetX': ['aod', 'detectorOffset', 'x'],
        'aodDetectorOffsetY': ['aod', 'detectorOffset', 'y'],
        'aodDetectorOffsetZ': ['aod', 'detectorOffset', 'z'],
        'aodDetectorOffsetXUnit': ['aod', 'detectorOffset', 'unit'],
        'aodDetectorOffsetYUnit': ['aod', 'detectorOffset', 'unit'],
        'aodDetectorOffsetZUnit': ['aod', 'detectorOffset', 'unit'],

        'aodStiffnessX': ['aod', 'stiffness', 'x'],
        'aodStiffnessY': ['aod', 'stiffness', 'y'],
        'aodStiffnessXUnit': ['aod', 'stiffness', 'unit'],
        'aodStiffnessYUnit': ['aod', 'stiffness', 'unit'],

        'aodDisplacementSensitivityX': ['aod', 'displacementSensitivity', 'x'],
        'aodDisplacementSensitivityY': ['aod', 'displacementSensitivity', 'y'],
        'aodDisplacementSensitivityXUnit': ['aod', 'displacementSensitivity', 'unit'],
        'aodDisplacementSensitivityYUnit': ['aod', 'displacementSensitivity', 'unit'],

        # pm variables
        'pmCornerFreqX': ['pm', 'cornerFreq', 'x'],
        'pmCornerFreqY': ['pm', 'cornerFreq', 'y'],
        'pmCornerFreqXUnit': ['pm', 'cornerFreq', 'unit'],
        'pmCornerFreqYUnit': ['pm', 'cornerFreq', 'unit'],

        'pmDetectorOffsetX': ['pm', 'detectorOffset', 'x'],
        'pmDetectorOffsetY': ['pm', 'detectorOffset', 'y'],
        'pmDetectorOffsetZ': ['pm', 'detectorOffset', 'z'],
        'pmDetectorOffsetXUnit': ['pm', 'detectorOffset', 'unit'],
        'pmDetectorOffsetYUnit': ['pm', 'detectorOffset', 'unit'],
        'pmDetectorOffsetZUnit': ['pm', 'detectorOffset', 'unit'],

        'pmStiffnessX': ['pm', 'stiffness', 'x'],
        'pmStiffnessY': ['pm', 'stiffness', 'y'],
        'pmStiffnessXUnit': ['pm', 'stiffness', 'unit'],
        'pmStiffnessYUnit': ['pm', 'stiffness', 'unit'],

        'pmDisplacementSensitivityX': ['pm', 'displacementSensitivity', 'x'],
        'pmDisplacementSensitivityY': ['pm', 'displacementSensitivity', 'y'],
        'pmDisplacementSensitivityXUnit': ['pm', 'displacementSensitivity', 'unit'],
        'pmDisplacementSensitivityYUnit': ['pm', 'displacementSensitivity', 'unit'],

        # aod tweebot camera variables
        'andorAodCenterX': ['aod', 'camera', 'andorCenter', 'x'],
        'andorAodCenterY': ['aod', 'camera', 'andorCenter', 'y'],
        'andorAodRangeX': ['aod', 'camera', 'andorRange', 'x'],
        'andorAodRangeY': ['aod', 'camera', 'andorRange', 'y'],
        'andorAodCenterXUnit': ['aod', 'camera', 'andorCenter', 'unit'],
        'andorAodCenterYUnit': ['aod', 'camera', 'andorCenter', 'unit'],
        'andorAodRangeXUnit': ['aod', 'camera', 'andorRange', 'unit'],
        'andorAodRangeYUnit': ['aod', 'camera', 'andorRange', 'unit'],

        'ccdAodCenterX': ['aod', 'camera', 'ccdCenter', 'x'],
        'ccdAodCenterY': ['aod', 'camera', 'ccdCenter', 'y'],
        'ccdAodRangeX': ['aod', 'camera', 'ccdRange', 'x'],
        'ccdAodRangeY': ['aod', 'camera', 'ccdRange', 'y'],
        'ccdAodCenterXUnit': ['aod', 'camera', 'ccdCenter', 'unit'],
        'ccdAodCenterYUnit': ['aod', 'camera', 'ccdCenter', 'unit'],
        'ccdAodRangeXUnit': ['aod', 'camera', 'ccdRange', 'unit'],
        'ccdAodRangeYUnit': ['aod', 'camera', 'ccdRange', 'unit'],

        # pm tweebot camera variables
        'andorPmCenterX': ['pm', 'camera', 'andorCenter', 'x'],
        'andorPmCenterY': ['pm', 'camera', 'andorCenter', 'y'],
        'andorPmRangeX': ['pm', 'camera', 'andorRange', 'x'],
        'andorPmRangeY': ['pm', 'camera', 'andorRange', 'y'],
        'andorPmCenterXUnit': ['pm', 'camera', 'andorCenter', 'unit'],
        'andorPmCenterYUnit': ['pm', 'camera', 'andorCenter', 'unit'],
        'andorPmRangeXUnit': ['pm', 'camera', 'andorRange', 'unit'],
        'andorPmRangeYUnit': ['pm', 'camera', 'andorRange', 'unit'],

        'ccdPmCenterX': ['pm', 'camera', 'ccdCenter', 'x'],
        'ccdPmCenterY': ['pm', 'camera', 'ccdCenter', 'y'],
        'ccdPmRangeX': ['pm', 'camera', 'ccdRange', 'x'],
        'ccdPmRangeY': ['pm', 'camera', 'ccdRange', 'y'],
        'ccdPmCenterXUnit': ['pm', 'camera', 'ccdCenter', 'unit'],
        'ccdPmCenterYUnit': ['pm', 'camera', 'ccdCenter', 'unit'],
        'ccdPmRangeXUnit': ['pm', 'camera', 'ccdRange', 'unit'],
        'ccdPmRangeYUnit': ['pm', 'camera', 'ccdRange', 'unit'],

        # bead
        'pmBeadDiameter': ['pm', 'beadDiameter'],
        'aodBeadDiameter': ['aod', 'beadDiameter'],
        'pmBeadDiameterUnit': ['pm', 'beadDiameterUnit'],
        'aodBeadDiameterUnit': ['aod', 'beadDiameterUnit'],

        # andor camera specifics
        'andorPixelSizeX': ['camera', 'andorPixelSize', 'x'],
        'andorPixelSizeY': ['camera', 'andorPixelSize', 'y'],
        'andorPixelSizeXUnit': ['camera', 'andorPixelSize', 'unit'],
        'andorPixelSizeYUnit': ['camera', 'andorPixelSize', 'unit'],

        # ccd camera specifics
        'ccdPixelSizeX': ['camera', 'ccdPixelSize', 'x'],
        'ccdPixelSizeY': ['camera', 'ccdPixelSize', 'y'],
        'ccdPixelSizeXUnit': ['camera', 'ccdPixelSize', 'unit'],
        'ccdPixelSizeYUnit': ['camera', 'ccdPixelSize', 'unit']
    }

    meta_key = key_mapper.get(key, None)

    # if the key is not there, use it as it is without nesting
    if meta_key is None:
        meta_key = [key]

    return meta_key


def convert_value_type(key, value):
    """
    Convert the value of a header key from string to the correct format.

    Args:
        key (string): header key to look up
        value (string): value to convert

    Returns:
        converted value
    """

    key_mapper = {
        # general stuff
        'isDataAveraged': 'bool',
        'nSamples': int,
        'samplingRate': int,
        'recordingRate': int,
        'measurementDuration': float,
        'timeStep': float,
        'deltaTime': float,
        'nBlocks': int,
        'viscosity': float,

        'laserDiodeTemp': float,
        'laserDiodeHours': float,
        'laserDiodeCurrent': float,

        'errors': 'errors',

        # aod variables
        'aodCornerFreqX': float,
        'aodCornerFreqY': float,

        'aodDetectorOffsetX': float,
        'aodDetectorOffsetY': float,
        'aodDetectorOffsetZ': float,

        'aodStiffnessX': float,
        'aodStiffnessY': float,

        'aodDisplacementSensitivityX': float,
        'aodDisplacementSensitivityY': float,

        # pm variables
        'pmCornerFreqX': float,
        'pmCornerFreqY': float,

        'pmDetectorOffsetX': float,
        'pmDetectorOffsetY': float,
        'pmDetectorOffsetZ': float,

        'pmStiffnessX': float,
        'pmStiffnessY': float,

        'pmDisplacementSensitivityX': float,
        'pmDisplacementSensitivityY': float,

        # aod tweebot camera variables
        'andorAodCenterX': float,
        'andorAodCenterY': float,
        'andorAodRangeX': float,
        'andorAodRangeY': float,

        'ccdAodCenterX': float,
        'ccdAodCenterY': float,
        'ccdAodRangeX': float,
        'ccdAodRangeY': float,

        # pm tweebot camera variables
        'andorPmCenterX': float,
        'andorPmCenterY': float,
        'andorPmRangeX': float,
        'andorPmRangeY': float,

        'ccdPmCenterX': float,
        'ccdPmCenterY': float,
        'ccdPmRangeX': float,
        'ccdPmRangeY': float,

        # bead
        'pmBeadDiameter': float,
        'aodBeadDiameter': float,

        # andor camera specifics
        'andorPixelSizeX': float,
        'andorPixelSizeY': float,

        # ccd camera specifics
        'ccdPixelSizeX': float,
        'ccdPixelSizeY': float,
    }

    if key in key_mapper:
        if key_mapper[key] == 'bool':
            return bool(strtobool(value))
        elif key_mapper[key] == 'errors':
            value = [int(error) for error in value.split('\t')]
            return value
        else:
            return key_mapper[key](value)
    else:
        return value


def get_standard_identifier(key):
    """
    Translate a header key to a unique identifier. This is neccessary as several versions of header keys are around.

    Args:
        key (string)

    Returns:
        string
    """

    # reduce number of variations: strip spaces
    # one could also change everything to lower case but that would decrease readability
    key = key.strip()

    key_mapper = {
        # general stuff
        'Date of Experiment': 'date',
        'measurement starttime': 'startTime',
        'data averaged to while-loop': 'isDataAveraged',

        'number of samples': 'nSamples',
        'Number of samples': 'nSamples',
        'nSamples': 'nSamples',

        'sample rate': 'samplingRate',
        'Sample rate (Hz)': 'samplingRate',
        'Sample rate': 'samplingRate',
        'sampleRate.Hz': 'samplingRate',

        'rate of while-loop': 'recordingRate',
        'duration of measurement': 'measurementDuration',
        'dt': 'timeStep',

        'timeStep': 'timeStep',
        'Delta time': 'deltaTime',

        'number of blocks': 'nBlocks',
        'nBlocks': 'nBlocks',

        'Viscosity': 'viscosity',
        'viscosity': 'viscosity',

        'Laser Diode Temp': 'laserDiodeTemp',
        'Laser Diode Operating Hours': 'laserDiodeHours',
        'Laser Diode Current': 'laserDiodeCurrent',

        'errors': 'errors',
        'start of measurement': 'startOfMeasurement',
        'end of measurement': 'endOfMeasurement',

        # aod variables
        'AOD horizontal corner frequency': 'aodCornerFreqX',
        'AOD vertical corner frequency': 'aodCornerFreqY',

        'AOD detector horizontal offset': 'aodDetectorOffsetX',
        'AOD detector vertical offset': 'aodDetectorOffsetY',

        'AOD horizontal trap stiffness': 'aodStiffnessX',
        'AOD vertical trap stiffness': 'aodStiffnessY',

        'AOD horizontal OLS': 'aodDisplacementSensitivityX',
        'AOD vertical OLS': 'aodDisplacementSensitivityY',

        # pm variables
        'PM horizontal corner frequency': 'pmCornerFreqX',
        'PM vertical corner frequency': 'pmCornerFreqY',

        'PM detector horizontal offset': 'pmDetectorOffsetX',
        'PM detector vertical offset': 'pmDetectorOffsetY',

        'PM horizontal trap stiffness': 'pmStiffnessX',
        'PM vertical trap stiffness': 'pmStiffnessY',

        'PM horizontal OLS': 'pmDisplacementSensitivityX',
        'PM vertical OLS': 'pmDisplacementSensitivityY',

        # aod tweebot variables
        'AOD detector x offset': 'aodDetectorOffsetX',
        'AOD detector y offset': 'aodDetectorOffsetY',

        'AOD trap stiffness x': 'aodStiffnessX',
        'AOD trap stiffness y': 'aodStiffnessY',

        'xStiffnessT2.pNperNm': 'aodStiffnessX',
        'yStiffnessT2.pNperNm': 'aodStiffnessY',

        'AOD trap distance conversion x': 'aodDisplacementSensitivityX',
        'AOD trap distance conversion y': 'aodDisplacementSensitivityY',

        'xDistConversionT2.VperNm': 'aodDisplacementSensitivityX',
        'yDistConversionT2.VperNm': 'aodDisplacementSensitivityY',

        'xCornerFreqT2.Hz': 'aodCornerFreqX',
        'xCornerFreqT2': 'aodCornerFreqX',
        'yCornerFreqT2.Hz': 'aodCornerFreqY',
        'yCornerFreqT2': 'aodCornerFreqY',

        'xOffsetT2.V': 'aodDetectorOffsetX',
        'yOffsetT2.V': 'aodDetectorOffsetY',
        'zOffsetT2.V': 'aodDetectorOffsetZ',

        # pm tweebot variables
        'PM detector x offset': 'pmDetectorOffsetX',
        'PM detector y offset': 'pmDetectorOffsetY',

        'PM trap stiffness x': 'pmStiffnessX',
        'PM trap stiffness y': 'pmStiffnessY',

        'xStiffnessT1.pNperNm': 'pmStiffnessX',
        'yStiffnessT1.pNperNm': 'pmStiffnessY',

        'PM trap distance conversion x': 'pmDisplacementSensitivityX',
        'PM trap distance conversion y': 'pmDisplacementSensitivityY',

        'xDistConversionT1.VperNm': 'pmDisplacementSensitivityX',
        'yDistConversionT1.VperNm': 'pmDisplacementSensitivityY',

        'xCornerFreqT1.Hz': 'pmCornerFreqX',
        'xCornerFreqT1': 'pmCornerFreqX',
        'yCornerFreqT1.Hz': 'pmCornerFreqY',
        'yCornerFreqT1': 'pmCornerFreqY',

        'xOffsetT1.V': 'pmDetectorOffsetX',
        'xOffsetT1': 'pmDetectorOffsetX',
        'yOffsetT1.V': 'pmDetectorOffsetY',
        'yOffsetT1': 'pmDetectorOffsetY',
        'zOffsetT1.V': 'pmDetectorOffsetZ',

        # aod tweebot camera variables
        'AOD ANDOR center x': 'andorAodCenterX',
        'AOD ANDOR center y': 'andorAodCenterY',
        'AOD ANDOR range x': 'andorAodRangeX',
        'AOD ANDOR range y': 'andorAodRangeY',

        'AOD CCD center x': 'ccdAodCenterX',
        'AOD CCD center y': 'ccdAodCenterY',
        'AOD CCD range x': 'ccdAodRangeX',
        'AOD CCD range y': 'ccdAodRangeY',

        # pm tweebot camera variables
        'PM ANDOR center x': 'andorPmCenterX',
        'PM ANDOR center y': 'andorPmCenterY',
        'PM ANDOR range x': 'andorPmRangeX',
        'PM ANDOR range y': 'andorPmRangeY',

        'PM CCD center x': 'ccdPmCenterX',
        'PM CCD center y': 'ccdPmCenterY',
        'PM CCD range x': 'ccdPmRangeX',
        'PM CCD range y': 'ccdPmRangeY',

        # bead
        'PM bead diameter': 'pmBeadDiameter',
        'diameterT1.um': 'pmBeadDiameter',

        'AOD bead diameter': 'aodBeadDiameter',
        'diameterT2.um': 'aodBeadDiameter',

        # andor camera specifics
        'ANDOR pixel size x': 'andorPixelSizeX',
        'ANDOR pixel size y': 'andorPixelSizeY',

        # ccd camera specifics
        'CCD pixel size x': 'ccdPixelSizeX',
        'CCD pixel size y': 'ccdPixelSizeY'
    }

    return key_mapper[key]