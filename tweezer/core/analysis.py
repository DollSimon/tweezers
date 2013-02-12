
"""
Analysis of Tweezer Experiments
"""

import numpy as np 
import pandas as pd 
import scipy as sci 
import matplotlib as mp 


class TweezerExperimentMetaData(dict):
    """
    The metadata of the tweezer experiment.
    """
    def __init__(self):
        dict.__init__(self)
        pass


class TweezerExperiment(object):
    """
    Analysis of a tweezer experiment. Holds the data, metadata of a tweezer experiment.
    """

    def __init__(self, **parameters):
        """
        __init__(**parameters)

        Initialise TweezerExperiment object to default and supplied parameter values.
        The supplied parameter values are in a dictionary 'parameters' with
        keys correspond to the parameter names.
        """

        ## Set default parameters
        
        # General physical parameters
        self.thermal_energy = 4.14 
        self.viscosity = 0.9e-9        

        # Parameters for the worm like chain models
        self.wlc_stretch_modulus = 1200;
        self.wlc_persistence_length = 53;


        self.metadata = TweezerExperimentMetaData()
        self.averaging_time = 10;
        self.lptime = 1000;
        self.savitzky_golay_time = 2000;
        self.acctime = 2500;
        self.L0 = 3077;
        self.thermal_energy = 4.14;
        self.nmPbp = 0.338;
        self.vhbinsize = 0.5;
        self.vhlow = -4.75;
        self.vhhigh = 24.75;
        self.PDtimeSD = 2;
        self.PDtime = 0.8;
        self.IntoFinP = 4;
        self.force_bin_size = 0.2
        self.force_bounds = (0, 15)     # boundaries for applied forces
        self.nfbinsize = 0.01;
        self.nflow = 0.3;
        self.nfhigh = 1.5;
        self.removedrift = 1;
        self.confint = 0.68269;
        self.mindL = 10;
        self.dtinterval = 1;
        self.velwin = 20;
        self.btcutoff = 1;
        self.nolateP = 1;


    def print_units(self):
        """
        Prints the units of the tweezer experiments in a formatted table.
        """
        
        units = self.units()

        for keys, values in units.items():
            print("{} : {}".format(keys, values))

    def _reference_units(self):
        """
        Contains a dictionary of all the units used in tweezer experiments.
        """
        reference_units = dict()
        reference_units = {   
                    'thermal_energy': 'pN * nm',
                    'wlc_persistence_length': 'nm',
                    'wlc_stretch_modulus': 'pN',
                    'viscosity': 'pN / nm^2 s',
                    'laser_diode_current': 'A',
                    'aod_andor_center_x': 'px',
                    'aod_andor_center_y': 'px',
                    'aod_andor_range_x': 'px',
                    'aod_andor_range_y': 'px',
                    'aod_ccd_center_x': 'px',
                    'aod_ccd_center_y': 'px',
                    'aod_ccd_range_x': 'px',
                    'aod_ccd_range_y': 'px',
                    'pm_andor_center_x': 'px',
                    'pm_andor_center_y': 'px',
                    'pm_andor_range_x': 'px',
                    'pm_andor_range_y': 'px',
                    'pm_ccd_center_x': 'px',
                    'pm_ccd_center_y': 'px',
                    'pm_ccd_range_x': 'px',
                    'pm_ccd_range_y': 'px',
                    'andor_pixel_size_x': 'nm',
                    'andor_pixel_size_y': 'nm',
                    'ccd_pixel_size_x': 'nm',
                    'ccd_pixel_size_y': 'nm',
                    'aod_detector_x_offset': 'V',
                    'aod_detector_y_offset': 'V',
                    'aod_trap_stiffness_x': 'pN/nm',
                    'aod_trap_stiffness_y': 'pN/nm',
                    'aod_trap_distance_conversion_x': 'MHz/px',
                    'aod_trap_distance_conversion_y': 'MHz/px',
                    'pm_detector_x_offset': 'V',
                    'pm_detector_y_offset': 'V',
                    'pm_trap_stiffness_x': 'pN/nm',
                    'pm_trap_stiffness_y': 'pN/nm',
                    'pm_trap_distance_conversion_x': 'V/px',
                    'pm_trap_distance_conversion_y': 'V/px',
                    'aod_bead_radius': 'um',
                    'pm_bead_radius': 'um',
                    'sampling_rate': 'Hz',
                    'number_of_samples': 'unitless',
                    'time_step': 's'}

        return reference_units

    def _print_reference_units(self):
        """
        Prints the reference units of the tweezer experiments in a formatted table.
        """
        reference_units = self._reference_units()

        for keys, values in reference_units.items():
            print("{} : {}".format(keys, values))
