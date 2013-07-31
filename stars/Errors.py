"""
Error module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
            Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

Error module for STARS.  Not currently in use.


"""

class Error:
    """STARS error message handler."""
    def __init__(self,string):
        so = "STARS Error: "+string
        print so
