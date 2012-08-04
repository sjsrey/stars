""" Messages.py
Message module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

This module contains messages for STARS users.


"""

class Message:
    def __init__(self,string):
        so = "STARS: "+string
        print so


class Error:
    """STARS error message handler."""
    def __init__(self,string):
        so = "STARS Error: "+string
        print so

def Opening():
        so = """
        STARS Copyright 2002, Sergio J. Rey

        STARS is free software and comes with ABSOLUTELY NO WARRANTY.
        You are welcome to redistribute it under certain conditions.
        Type 'license()' for more infomration."""
        print so

def license():
        so = """
        This software is distributed under the terms of the GNU GENERAL
        PUBLIC LICENSE Version 2, June 1991.  The terms of this license
        are in a file called COPYING which you should have received with
        this software.

        If you have not received a copy of this file, you can obtain one
        via WWW at http://www.gnu.org/copyleft/gpl.html, or by writing to:

           The Free Software Foundation, Inc.,
           59 Temple Place - Suite 330, Boston, MA 02111-1307, USA."""
        print so


def shelp(method=None):
    """Prints help information for STARS methods."""
    if method:
        print method.__doc__
        print "For help on classes: from ModuleName import *"
    else:
        print """shelp useage:
        shelp(ModuleName)

        where ModuleName is one of:
            Esda
            Inequality
            Mobility
            Markov
            SpEcon"""

 



