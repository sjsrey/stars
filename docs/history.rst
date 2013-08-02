**************************
STARS History and Road Map
**************************


Where we have come from
=======================

Development on STARS was put on hold while the library
`PySAL <http://code.google.com/p/pysal/>`_
was given priority focus. Many of the analytical methods first implemented in
STARS were moved into the PySAL library during this time. Until PySAL was
stable and had gone through several release versions, the plan had always been
to keep STARS on the back burner.  Once PySAL was stable, the idea was to
rebuild a new version of STARS that rested on PySAL.

Another reason behind the long period since the last STARS update had to do
with the thorny nature of heterogeneous data underlying space-time analysis.
There were no standards for this data, and much exploratory programming was
done by various people around the STARS project in this regard, but nothing
ever seemed completely satisfactory. 

Where we are going
==================

Fortunately, since this period the library
`pandas <http://pandas.pydata.org>`_ 
has appeared on the scene and offers a very
flexible, efficient and well documented library for dealing with this type of
data. As such, the current STARS project is planning on making heavy use of
pandas for data management issues which would free up development time to
focus on some of the space-time analytical and visualization related issues.

Moving forward, there are short run and long run plans for STARS development.
In the short run, there have been many requests for a version of STARS that
runs on Windows 7. Because the last stable release relied on numeric (pre
numpy days), some effort must be directed at refactoring the last version to
meet these immediate needs.

In the longer term, however, the focus will be on a completely new rewrite of
STARS that rests on PySAL and draws on the  pandas library. STARS will also
serve as somewhat of a testing ground for new space-time methods that
eventually will be moved into the spatial_dynamics library of PySAL.

