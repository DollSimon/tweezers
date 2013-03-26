.. Tweezer documentation master file, created by
   sphinx-quickstart on Sat Dec 22 03:29:38 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

The Tweezer Code Docs!
===================================

Tools to analyse data of dual-trap optical tweezer experiments. 

This is to test :cite:`Revyakin:2003dm` all the features of cites.

Aim
====

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


.. todo:: 
   
   Figure out why tikz extension does not work :bbissue:`1`


Tikz test:
===========

.. tikz:: [>=latex',dotted,thick] \draw[->] (0,0) -- (1,1) -- (1,0)
   -- (2,0);
   :libs: arrows


.. tikz:: An Example Directive with Caption
   \draw[thick,rounded corners=8pt]
   (0,0)--(0,2)--(1,3.25)--(2,2)--(2,0)--(0,2)--(2,2)--(0,0)--(2,0);
   

This is a test whether this all works. This

   :bbissue:`1`

is almost cool.


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
