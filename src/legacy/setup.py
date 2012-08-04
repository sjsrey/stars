"""
setup script module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

setup scripts for STARS.


"""

from distutils.core import setup
import py2app
import os

setup(
    name='STARS',
    version='0.8.2',
    description='Space Time Analysis of Regional Systems',
    long_description='Space Time Analysis of Regional Systems',
    url='http://stars-py.sf.net',
    author="Sergio J. Rey",
    author_email='sjrey@users.sf.net',
    app=['starsgui.py'],
    options={"py2app": {"argv_emulation":True,
            "iconfile": 'stars.icns'}},
    data_files=[('',['stars.icns','splash.gif','credits.txt','COPYING']),
                ('data',['data/csiss.prj','data/csiss.dht',
                    'data/csiss.dat','data/us48.gis',
                    'data/states48.gal',
                    'data/caPCR.csv',
                    'data/caPOP.csv',
                    'data/caTS.csv',
                    'data/california.dbf',
                    'data/california.shp',
                    'data/california.shx',
                    'data/california.csv',
                    'data/caJoinCS.csv',
                    'data/caJoinCSTS.csv',
                    'data/Cali1.gal'
                    ])]
)

#,'doc/starsqs.pdf'

