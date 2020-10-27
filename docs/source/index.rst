Welcome to the Tweezers documentation!
======================================

The starting point for using this library are:

* :class:`.TweezersData` - represents a single dataset
* :class:`.TweezersDataCollection` - is a collection of :class:`.TweezersData` and provides methods to load multiple datasets from disk
* :class:`.TweezersAnalysis` - represents an analyzed dataset (e.g. when using the Segment Selector tool), can also be created manually
* :class:`.TweezersAnalysis`  - is a collection of :class:`.TweezersAnalysis` and provides methods to load datasets from disk

Contents:

.. toctree::
   :maxdepth: 3

   tweezers

How to build the SegmentSelector
--------------------------------

Open a terminal (or command prompt on Windows) and navigate to the `tweezers \ SegmentSelector` directory.

From there, run `buildSegmentSelector.sh` (or `buildSegmentSelector.bat` on Windows) to build the tool. The resulting executable
is located in `tweezers \ SegmentSelector \ dist`.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

