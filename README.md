# Tweezer - Data Analysis Tools for Single Molecule Experiments

A python package containing all the relevant files for tweezer data analysis.

### `TODO`

* recalibrate time series of tweezer files with simple Lorentz fit
* determine the optimum fit range for Lorentz fit
* develop / port more sophisticated calibration methods to this code
    1. fitting power spectra with hydrodynamic and aliasing corrections for single beads
    2. using MLE (maximum likelihood methods) to robustly fit the data
    3. applying corrections for two beads in close proximity
    4. using Allan variance as a second way to calibrate the time series
    5. using active calibration methods (oscillation)
