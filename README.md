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


### Installation for users

On the command line, go to the `tweezers` directory and run `pip install .` (don't forget the `.`).


### Installation for developers

On the command line, go to the `tweezers` directory and run `pip install -e .`. This will not copy the package files to your Python path but create a link instead. This allows you to run modifications to the package files without having to reinstall everything.

Note that a modified package has to be reloaded though for the changes to take effect. When using IPython (in the terminal or as a Jupyter notebook), use the `autoreload`-extension. Run the following code before importing packages when starting up your IPython session or notebook:

```
%load_ext autoreload
%autoreload 2
```

This will reload all packages everytime you run code. There also is the option to only reload specified packages with `%autoreload 1` and `%aimport <package name>` but this does not allow you to use aliases for modules (like `import tweezers as tz`).


## Build the docs

To build the docs, simply open a terminal, go to the `docs` directory and use the following commands.

```bash
make apidoc
make html
```

Then open `docs/build/index.html` with your browser and you're done.