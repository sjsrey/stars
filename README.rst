#####
STARS
#####

Space-Time Analysis of Regional Systems: a package for exploratory space-time
data analysis.

.. image:: web/linkWin.png 
   :width: 800
   :height: 400

The current version of STARS is based on a refactoring to move from Numeric
to Numpy. This version should work on the following platforms

- Linux
- Windows
- Mac 

Installation
============

Vagrant under Ubuntu
--------------------

Build and run the box:

1. `sudo apt-get install virtualbox`
2. `sudo apt-get install vagrant`
3. `vagrant up`
4. `vagrant ssh`
5. `cd stars`
6. `python -i starsgui.py -i`

The initial build will take some time, however future boots of the VM
will be fast:

1. `vagrant up`
4. `vagrant ssh`
5. `cd stars`
6. `python -i starsgui.py -i`



Source
------

Currently only source installs are available:

1. Download source archive from master_
2. ``cd stars-master/stars``
3. ``python -i starsgui.py``

Mac OS X Notes
--------------

There is a bug with Tk under Mavericks resulting in slow updates of the views.
Installing `Active Python <http://www.activestate.com/activepython>`_ is a work-around.

The Tk bug has been fixed in Yosemite. 

Windows Notes
-------------

STARS has been tested on the following versions:

- Windows XP
- Windows 7
- Windows 8
- Windows 8.1

Road Map
========

For more details on the plans for development, see
`STARS History and Road Map <https://github.com/sjsrey/stars/blob/master/docs/history.rst>`_.

Links
=====

* STARS previous home_ 
* STARS downloads_
* PySAL_ 


.. _master: https://github.com/sjsrey/stars/archive/master.zip
.. _home: http://regionalanalysislab.org
.. _downloads: http://regionalanalysislab.org/?n=Download
.. _PySAL: http://pysal.org
