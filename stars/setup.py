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
import py2exe
import os


includes = []
excludes = []
packages = []
dll_excludes = [
		'mswsock.dll', 'powerprof.dll'
]

mydata_files = [
		(' ', ['stars.ico', 'splsh.gif', 'README.txt', 'license.txt', 'credits.txt', 'COPYING.txt']),
		('data', ['data/csiss.prj','data/csiss.dht',
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
					]
		)
]

setup(
		console=[{		
				'script': ('stars', ['starsgui.py']),
				'name': 'STARS',
				'version': '0.8.2',
				'description': 'Space Time Analysis of Regional Systems',
				'url': 'http://stars-py.sf.net',
				'author': 'Sergio J. Rey',
				'author_email': 'sjrey@users.sf.net',
		}],
		data_files=mydata_files,
		options={
				'py2exe': {
						'compressed': 2,
						'optimize': 2,
						'includes': includes,
						'excludes': excludes,
						'dll_excludes': dll_excludes,
						'bundle_files': 1,   # 1 = .exe; 2 = .zip; 3 = separate
						'dist_dir': 'dist',  # Put .exe in dist/
				}
		},
		zipfile=None,
		windows=[{
				'script': 'starsgui.py',
				'icon_resources': [(0, 'stars.ico')],
		}]
)

#, 'doc/starsqs.pdf'