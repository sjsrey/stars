"""
setup script module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

setup scripts for STARS.


"""

from distutils.core import setup
import py2app
import os

setup(
    name='ProjectMaker',
    version='0.8.2',
    app=['projectMaker.py'],
    options={"py2app": {"argv_emulation":True,
            "iconfile": 'stars.icns'}},
    data_files=[('',['stars.icns','splash.gif','credits.txt','COPYING']),
                ('data',['data/csiss.prj','data/csiss.dht',
                    'data/csiss.dat','data/us48.gis',
                    'data/states48.gal'])]
)
                
#('doc',['doc/starsqs.pdf'])]
