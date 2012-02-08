
========================================================
A brief (and incomplete) intro to the ``Pandas`` library
========================================================

----

Background and context
======================

* `Wes McKinney <http://wesmckinney.com>`_ is the main developer (the only one?)
* Development stated at AQR Capital Management, circa 2008
* Quantitative finance :math:`\rightarrow` Focus on time series (not much
  intrinsically spatial)

Features
--------

* "Data structures for labelled data"
* Numpy based
* Data alignment and easy (and fast) reshaping
* Missing value support
* Some statistical operators built-in (averages, std, correlation
  coefficients)

----

Data Structures - Series
========================

* Labelled vector: np.array of (n,) with an index
* May be created from 

    * Python dict
    * An ndarray
    * A scalar

* Supports basic operations like ``mean()``, ``std()`` or ``count()`` 
* ``index`` can be any id list
* Built-in matching of indices when combining them

----

Data Structures - DataFrame
===========================

* Compilation of series, indexed by columns as well.
* May also be created from the same objects (dict, ndarray, scalar) and has
  two indices, the ``index`` and the ``columns``.
* Matching extends to columns as well when combining DataFrame's
* Adding and removing extra columns
* Other features:  hierarchical indexing, pivoting and reshaping, ``groupby()`` (group data by identifiers and perform aggregation or
  transformations on them).

``panel`` structure
-------------------
* (Indexed) compilation of DataFrame's with a third index controlling for
  time (``index``, ``columns``, ``time``)

----

Useful operations
=================

Data I/O
--------

Built-in functions to read and write:

    * From clipboard
    * ``csv`` and other text files
    * ``html``
    * Excel files
    * HDF5 (PyTables)

Subsetting, Slicing and Joining
-------------------------------

* Easy and efficient **subsetting** of data frames, very much in R style.
* Via the attribute ``ix``, data frames may be accessed the same way as a numpy array. For example, ``df.ix[i, :]`` will give you the i-th row of the data frame ``df``.
* Using the built-in matching functionality, ``pandas`` can **join** data frames by index or by columns with several sql-like options (inner, outer...).

----

Further resources
=================

* Official `documentation <http://pandas.sourceforge.net/basics.html>`_
* PyHPC 2011 `paper <http://wesmckinney.com/blog/?p=330>`_
* Videos: 
  
    * `Lightning talk <http://www.youtube.com/watch?v=3vrCCjmVnIk>`_
    * `PyCon 2010
      <http://python.mirocommunity.org/video/1531/pycon-2010-python-in-quantitat>`_
    * `NYC Python meetup group talk <http://wesmckinney.com/blog/?p=437>`_ (1/10/2012)


----

Demo time
=========

