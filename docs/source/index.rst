.. Tweezer documentation master file, created by
   sphinx-quickstart on Sat Dec 22 03:29:38 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The Tweezer Code Docs!
======================

Tools to analyse data of dual-trap optical tweezer experiments. 

Aim
===

A user of this code base should be able to:

* parse raw data files in different formats into common python interface
* extract meaningful plots out of the raw data
* link a raw data item to the corresponding meta data
* recalibrate the thermal calibration files with more accurate power spectral methods
* zoom and select certain parts of the raw data for later analysis
* convert the raw data into a secure and fast and global saving option (e.g. hdf5)
* address variables by short and long form of there names
* easily look up relevant physical units associated with the variables
* exchange relevant data with the R programming language in order to use knitr for an overview template   
* calculate relevant quantities for single molecule experiments using optical tweezers
* simulate the behaviour of certain aspects of a single molecule system
* easily extend the functionality of this code by following the examples and reading the docs
* do all this from a convenient command line interface or from within ipyhton

Overview
========

.. autosummary::

    tweezer
    tweezer.analysis
    tweezer.bot
    tweezer.cli
    tweezer.core
    tweezer.db
    tweezer.dual
    tweezer.ixo
    tweezer.learn
    tweezer.lux
    tweezer.math
    tweezer.noise
    tweezer.physics
    tweezer.polymer
    tweezer.rnap
    tweezer.simulate
    tweezer.single
    tweezer.statistics

Contents:

.. toctree::
   :maxdepth: 3

   installation
   usage
   modules
   References


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. bibliography:: test.bib


.. todolist::
