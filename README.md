# Tweezers - Data Analysis Tools for Single Molecule Experiments

A python package containing all the relevant files for tweezers data analysis.

## `TODO`

* recalibrate time series of tweezers files with simple Lorentz fit [mostly done]
* determine the optimum fit range for Lorentz fit
* develop / port more sophisticated calibration methods to this code
    1. fitting power spectra with hydrodynamic and aliasing corrections for single beads
    2. using MLE (maximum likelihood methods) to robustly fit the data
    3. applying corrections for two beads in close proximity
    4. using Allan variance as a second way to calibrate the time series
    5. using active calibration methods (oscillation)


## Download

Get the code by either cloning it via e.g. SourceTree or download the entire repository using the Downloads section (on the left) and click on "Download repository" (or get the latest committed / tagged version).

## Installation

### Installation for users

#### Create environment

If you use various Python software, don't want to break dependencies and use `conda` to organize environments, follow these steps to create a environment into which the software will be installed.

Otherwise, skip this step

```
conda config --add channels conda-forge
conda create --name tweezers python=3.6
```

If you are planning to use Jupyter Notebooks, you have to choose whether you want to run Jupyter from within this environment or use it as an available kernel for Jupyter running from another (e.g. the base-) environment. In the latter case, you have to install `nb_conda_kernels` to the environment from which you run the Jupyter Notebook.

So, e.g. in your base-environment, install `jupyter` and `nb_conda_kernels`.

```
conda install jupyter nb_conda_kernels
```

To install the Jupyter NbExtensions (for table of contents etc.), run the following in the environment, from which you're running the Jupyter Notebook Server.

```
conda install jupyter_contrib_nbextensions
```


#### Installing the package

If you are using multiple environment, switch to the one you want to use, e.g. `tweezers` by running `conda activate tweezers`.

On the command line, go to the `tweezers` directory and run `pip install -e .` (don't forget the `.`).

Note that this will install the package in the development mode and not copy its content to the Python path but create a link to your current folder instead. This allows easier updating of the code via e.g. git.


#### Jupyter Configuration

If you plan to use Jupyter Notebooks, you might want to set the default directory in which to store these. To do that, open a terminal and run `jupyter-lab --generate-config` which will create a file `~/.jupyter/jupyter_notebook_config.py`. In there, look for the line `#c.NotebookApp.notebook_dir = ''`, adjust the path, uncomment the line and save the file.
You can now run Jupyter from the terminal with `jupyter lab` and use it in the browser.


### Notes for developers

Installing the package using the `-e` option for `pip` is good for development since you can have the code where ever you like for development. But keep in mind that during an interactive session, a modified package has to be reloaded for the changes to take effect. When using IPython (in the terminal or as a Jupyter notebook), use the `autoreload`-extension. Run the following code before importing packages when starting up your IPython session or notebook:

```
%load_ext autoreload
%autoreload 2
```

This will reload all packages everytime you run code. There also is the option to only reload specified packages with `%autoreload 1` and `%aimport <package name>` but this does not allow you to use aliases for modules (like `import tweezers as tz`).


### Troubleshooting


#### Matplotlib backend

```text
Python is not installed as a framework. The Mac OS X backend will not be able to function correctly if Python is not installed as a framework.
```

If you get an error message like above, change the default backend of `matplotlib`. Open a terminal window and run the following command.

```bash
echo "backend: Qt5Agg" > ~/.matplotlib/matplotlibrc
```


#### Matplotlib, LaTeX and Jupyter

When using LaTeX in a Jupyter Notebook and you get an error message like

```text
No such file or directory: 'latex': 'latex'
```

it means that Jupyter does not load all the environment path variables. Manually add the path to the latex executable to the Jupyter path variable. Add the following to your `.bash_profile`:

```bash
export JUPYTER_PATH="/Library/TeX/texbin/:$JUPYTER_PATH"
```

and replace the path by the proper one (e.g. run `which latex` and use that path).


## Build the docs

To build the docs, simply open a terminal, go to the `docs` directory and use the following commands.

```bash
make apidoc
make html
```

Then open `docs/build/index.html` with your browser and you're done.