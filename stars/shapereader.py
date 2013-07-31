"""
Reading ArcView shapefiles for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):   Serge Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:
Parsing of shapefiles. Based on modifications of original code by Luc Anselin (lucshape5.py)

"""


from struct import *
import time


# constants for shape types
SHP_POINT = 1
SHP_POLYGON = 5

class shape:
    """
    Class shape is the basic class to handle
    ESRI format shapefile
    Usage: shape(filename)
    The class initializes an object that has 4 attributes:
        filename: the name of the original shape file
        shptype: the type of shape file (1 point, 5 polygon)
        shpbox: an object of class bbox, i.e., 
                     a list of floats containing the shape bounding box
                     (Xmin,Ymin,Xmax,Ymax)
        shplist: a list of lists for each record
                    a. for polygons: (1) a bbox list of floats containing the
                    record bounding box (2) a list of offsets of the
                    points in each part, 0 for a single part (3) a
                    list of floats of tuples for (X, Y), with the first and last
                    pair being identical (ESRI format)
               b. for points: a list of floats for X,Y
    Methods:
        summary: summary of file contents (listing only)
        parttest: test for polygon records with multiple parts
    """
    def __init__(self,filename):
        """
        Initializes only, does nothing else, specific file input
        is handled by subclasses
        """
        self.filename = filename
        self.shptype = 0
        self.shpbox = bbox()
        self.shplist = []

    def summary(self):
        """
        Summary is a method associated with an object
        of class shape and  its subclasses.
        It provides a listing of shape file characteristics:
            file name, type and number of records.
        """
        print "======================="
        print "Shape File Name: " + str(self.filename)
        if self.shptype == SHP_POLYGON:
            print "Type: Polygon"
        elif self.shptype == SHP_POINT:
            print "Type: Point"
        print "Number of records: " + str(len(self.shplist))
        print "Bounding box:"
        print "   Xmin, Ymin:  " + ",".join(["%.8f" % i for i in self.shpbox[:2]])
        print "   Xmax, Ymax:  " + ",".join(["%.8f" % i for i in self.shpbox[2:]])
        print "======================="
            
    def parttest(self):
        """
        Parttest is a method associated with an object
        of class shape and its subclasses.
        It returns a list
        containing the index numbers
        (starting at 0) of the polygon shapes that consist
        of multiple parts.
        Returns empty list for point shape files.
        """
        multipart = []
        if self.shptype == SHP_POINT:
            return multipart
        for  i in range(len(self.shplist)):
            if len(self.shplist[i][1]) > 1:
                multipart.append(i)
        return multipart
        
    def shp2txt(self,outfile):
        pass
        # list contents of shape file to text file
        
    def shp2shp(self,outfile):
        pass
        # write contents of a shape object to ESRI shape file format
        # will require access to dbf and create shx as well
        
    def shp2xml(self,outfile):
        pass
        # list contents of shape file to xml file
        
    def shpsubset(self):
        pass
        # create a subset of  an existing shape object
        
    def shpcentral(self):
        pass
        # compute central point and add to dbf
        
    def shpcentroid(self):
        pass
        # compute centroid and add to dbf
        
    def shparea(self):
        pass
        # compute area and add to dbf
        
    def shpperimeter(self):
        pass
        # compute perimeter and add to dbf

class shapefile(shape):
    """
    Class shapefile is the basic class to read the contents of an
    ESRI format shapefile. It inherits common functionality from
    class shape
    Usage: shapefile(filename)
    Initialization is done by the base class: shape
    Note: other methods may be added to read and construct
    shape objects from ascii input and/or other formats; all methods
    that apply to the resulting shape objects are handled in the superclass
    Methods:
        shpopen: open the SHP file and read contents
    """
    def __init__(self, filename):
        """
        initialization initializes all attributes
        and calls shpopen method 
        """
        shape.__init__(self, filename)
        
        # parse the file name to assess type
        # first case: shp file
        self.shpopen()
        
        # text input file, may require key
        # xml? input file
        
    def shpopen(self):
        """
        open method reads shape file header and extracts type and
        bounding box. Next it reads the rest of the file, and, for each
        record, extracts the elements of the shplist.
        """
        try:
            f = open(self.filename, 'rb')
        except IOError:
            "Error: Make sure file is in working directory"
            return 1                    # TODO: need to handle error return
        shpread = f.read(100)        # first 100 bytes contain header
        shplen = unpack('>l',shpread[24:28])   # length of file in words
        flength = shplen[0]*2 - 100                 # convert to bytes and take out header
        self.shptype = unpack('<l',shpread[32:36])[0]   # type of shape file
#        self.shpbox = list(unpack('<dddd',shpread[36:68]))   # bounding box as list
        self.shpbox = bbox(list(unpack('<dddd',shpread[36:68])) )  # bounding box as bbox
        i = 0
        shpread = f.read(flength)
        if self.shptype == SHP_POLYGON:
            while i < flength:
                reclist=[]
                # bounding box
#                rbox=list(unpack('<dddd',shpread[i+12:i+44]))
                rbox=bbox(list(unpack('<dddd',shpread[i+12:i+44])))    # as bbox            
                reclist.append(rbox)
                # number of parts
                rnumpart=unpack('<l',shpread[i+44:i+48])[0]
                # total number of points
                rnumpt = unpack('<l',shpread[i+48:i+52])[0]
                h = i + 52 + rnumpart*4
                eater = '<' + 'l'*rnumpart
                # list with pointers to parts
                recpart=list(unpack(eater,shpread[i+52:h]))
                reclist.append(recpart)
                eater = '<' + 'dd'*rnumpt
                i = h + rnumpt*16
                # list with coordinates
                recpt = list(unpack(eater,shpread[h:i]))
#                reclist.append(recpt)
                #reclist.append([(recpt[ii],recpt[ii+1]) for ii in range(0,rnumpt*2,2) ]) # as list of tuples
                reclist.append([(recpt[ii],recpt[ii+1]) for ii in range(0,len(recpt),2) ]) # as list of tuples
                self.shplist.append(reclist)
                
        elif self.shptype == SHP_POINT:
            while i < flength:
                # for each record X,Y
                h = i + 28
                recpt = list(unpack('<dd',shpread[i+12:h]))
#                self.shplist.append(recpt)
                self.shplist.append([(recpt[ii],recpt[ii+1]) for ii in range(0,len(recpt),2)]) # as list of tuples
                i = h
        
        f.close()
        
    def txt2shp(self):
        pass
        # read and create shape from text file
        
    def xml2shp(self):
        pass
        # read and create shape file from xml
        
class gridshape(shape):
    """
    class to create shapes from grid info
    """
    
    def __init__(self,filename):
        pass
        
class bbox(list):
    """
    class for bounding box
    """
    
    def bbinside(self,bbother):
        chflag = 0
        if (self[0] >= bbother[0]) and (self[1] >= bbother[1]) and (self[2] <= bbother[2]) and (self[3] <= bbother[3]):
            chflag = 1
        return chflag
        
    def bbenclose(self,bbother):
        chflag = 0
        if (self[0] <= bbother[0]) and (self[1] <= bbother[1]) and (self[2] >= bbother[2]) and (self[3] >= bbother[3]):
            chflag = 1
        return chflag
        
    def bbcommon(self,bbother):
        chflag = 0
        if not ((bbother[2] < self[0]) or (bbother[0] > self[2])):
            if not ((bbother[3] < self[1]) or (bbother[1] > self[3])):
                chflag = 1
        return chflag
            
        
        
if __name__ == "__main__":
    fname = raw_input("Enter the shape file name (include .shp): ")
    t0 = time.time()
    test = shapefile(fname)
    t1 = time.time()
    print "-------------------------------------"
    print "time elapsed: " + str(t1-t0)
    test.summary()
    multipart = test.parttest()
    print "multiple parts " + str(multipart)
#various and sundry things to print out
#    print "filename is " + str(test.filename)
#    print "shape type is " + str(test.shptype)
#    print "bounding box is " + str(test.shpbox)
    print "first shape \n" + str(test.shplist[0])
    nshp = len(test.shplist)
    print "last shape \n" + str(test.shplist[nshp-1])
#    for i in range(nshp):
#        print i+1
#        print "bounding box \n" + str(test.shplist[i][0])
#        print "parts list \n" + str(test.shplist[i][1])
#        print "point list \n" + str(test.shplist[i][2])

    bobox = test.shpbox
    print str(bobox)
    print str(type(bobox))
    a = test.shplist[0][0]
    print str(a)
    aa = bbox(a)
    print str(aa)
    print str(type(aa))
    
        
    

