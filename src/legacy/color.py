"""
Color scheme classes for map views 
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

This module creates the colorschemes used for different views within STARS.
The color schemes are adapted from colorbrewer:
http://www.personal.psu.edu/faculty/c/a/cab38/ColorBrewerBeta2.html
"""

class ColorSchemes:
    """Color scheme manager"""
    def __init__(self):
        self.schemes ={}

    def addScheme(self,scheme):
        key = scheme.key
        self.schemes[key] = scheme

    def getScheme(self,device,legendType,nColors):
        key = device,legendType,nColors
        schemes = self.schemes
        if schemes.has_key(key):
            return schemes[key]
        else:
            print "No such colorScheme defined:",key
            return None
    def getSchemes(self):
        """Returns all defined ColorSchemes"""
        schemes = self.schemes
        keys =   schemes.keys() 
        keys.sort()
        return [ schemes[key] for key in keys]


class ColorScheme:
    """Individual color schemes"""
    def __init__(self,legendType,rgb,device,manager):
        self.legendType = legendType
        self.rgb = rgb
        self.device = device
        self.colors = self.tkrgb()
        self.nColors = len(self.colors)
        self.key = device,legendType,self.nColors
        self.manager = manager
        self.manager.addScheme(self)

    def tkrgb(self):
        tkrgb = [ "#%02X%02X%02X" % tuple(rgb) for rgb in self.rgb ] 
        return tkrgb

    def summary(self):
        print "Scheme Definition:",self.key


colorSchemes = ColorSchemes()

# qualitative 2 all
s=[
   [228,26,28],
   [55,126,184]
]
ColorScheme("qualitative",s,'projector',colorSchemes)
ColorScheme("qualitative",s,'laptop',colorSchemes)
ColorScheme("qualitative",s,'desktop',colorSchemes)

# qualitative 3 all
s=[
[228,26,28],
[55,126,184],
[77,175,74]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)


# qualitative 4 all
s=[
[228,26,28],
[55,126,184],
[77,175,74],
[152,78,163]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)


# qualitative 5 all
s=[
[228,26,28],
[55,126,184],
[77,175,74],
[152,78,163],
[255,127,0]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)


# qualitative 6 all
s=[
[228,26,28],
[55,126,184],
[77,175,74],
[152,78,163],
[255,127,0],
[255,255,51]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)

# qualitative 7 all
s=[
[228,26,28],
[55,126,184],
[77,175,74],
[152,78,163],
[255,127,0],
[255,255,51],
[166,86,40]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)

# qualitative 8 all
s=[
[228,26,28],
[55,126,184],
[77,175,74],
[152,78,163],
[255,127,0],
[255,255,51],
[166,86,40],
[247,129,191]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)


# qualitative 9 all
s=[
[228,26,28],
[55,126,184],
[77,175,74],
[152,78,163],
[255,127,0],
[255,255,51],
[166,86,40],
[247,129,191],
[153,153,153]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)


# qualitative 10 all
s=[
[166,206,227],
[31,120,180],
[178,223,138],
[51,160,44],
[251,154,153],
[227,26,28],
[253,191,111],
[255,127,0],
[202,178,214],
[106,61,154]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)

# qualitative 11 all
s=[
[166,206,227],
[31,120,180],
[178,223,138],
[51,160,44],
[251,154,153],
[227,26,28],
[253,191,111],
[255,127,0],
[202,178,214],
[106,61,154],
[255,255,153]
]
ColorScheme("qualitative",s,"projector",colorSchemes)
ColorScheme("qualitative",s,"laptop",colorSchemes)
ColorScheme("qualitative",s,"desktop",colorSchemes)

# sequential 2 all
s=[
   [228,26,28],
   [55,126,184]
]
ColorScheme("sequential",s,'projector',colorSchemes)
ColorScheme("sequential",s,'laptop',colorSchemes)
ColorScheme("sequential",s,'desktop',colorSchemes)

# sequential 3 laptop
s=[
[255,255,204],
[161,218,180],
[65,182,196]
]
ColorScheme("sequential",s,"laptop",colorSchemes)
ColorScheme("sequential",s,"desktop",colorSchemes)
ColorScheme("sequential",s,"projector",colorSchemes)




# sequential 4 laptop
s=[
[255,255,204],
[161,218,180],
[65,182,196],
[34,94,168]
]
ColorScheme("sequential",s,"laptop",colorSchemes)
ColorScheme("sequential",s,"desktop",colorSchemes)
ColorScheme("sequential",s,"projector",colorSchemes)



# sequential 5 lappie
s=[
[255,255,204],
[161,218,180],
[65,182,196],
[44,127,184],
[37,52,148]
]
ColorScheme("sequential",s,"laptop",colorSchemes)
ColorScheme("sequential",s,"desktop",colorSchemes)
ColorScheme("sequential",s,"projector",colorSchemes)


# sequential 6 lappie
s=[
[255,255,204],
[199,233,180],
[127,205,187],
[65,182,196],
[44,127,184],
[37,52,148]
]
ColorScheme("sequential",s,"laptop",colorSchemes)
ColorScheme("sequential",s,"desktop",colorSchemes)
ColorScheme("sequential",s,"projector",colorSchemes)

# sequential 7 screens
s=[
[255,255,204],
[199,233,180],
[127,205,187],
[65,182,196],
[29,145,192],
[34,94,168],
[12,44,132]
]
ColorScheme("sequential",s,"laptop",colorSchemes)
ColorScheme("sequential",s,"desktop",colorSchemes)
ColorScheme("sequential",s,"projector",colorSchemes)

# diverging 3 screens
s = [
[252,141,89],
[255,255,191],
[145,207,96]
]
ColorScheme("diverging",s,"laptop",colorSchemes)
ColorScheme("diverging",s,"desktop",colorSchemes)
ColorScheme("diverging",s,"projector",colorSchemes)


# diverging 4 screens
s = [
[215,25,28],
[253,174,97],
[166,217,106],
[26,150,65]
]
ColorScheme("diverging",s,"laptop",colorSchemes)
ColorScheme("diverging",s,"desktop",colorSchemes)
ColorScheme("diverging",s,"projector",colorSchemes)

# diverging 4 screens
s = [
[215,25,28],
[253,174,97],
[166,217,106],
[26,150,65]
]
ColorScheme("diverging",s,"laptop",colorSchemes)
ColorScheme("diverging",s,"desktop",colorSchemes)
ColorScheme("diverging",s,"projector",colorSchemes)


# diverging 5 screens
s = [
[215,25,28],
[253,174,97],
[255,255,191],
[166,217,106],
[26,150,65]
]
ColorScheme("diverging",s,"laptop",colorSchemes)
ColorScheme("diverging",s,"desktop",colorSchemes)
ColorScheme("diverging",s,"projector",colorSchemes)

# diverging 6 screens
s = [
[215,48,39],
[252,141,89],
[254,224,139],
[217,239,139],
[145,207,96],
[26,152,80]
]
ColorScheme("diverging",s,"laptop",colorSchemes)
ColorScheme("diverging",s,"desktop",colorSchemes)
ColorScheme("diverging",s,"projector",colorSchemes)

# diverging 7 screens
s = [
[215,48,39],
[252,141,89],
[254,224,139],
[255,255,191],
[217,239,139],
[145,207,96],
[26,152,80]
]
ColorScheme("diverging",s,"laptop",colorSchemes)
ColorScheme("diverging",s,"desktop",colorSchemes)
ColorScheme("diverging",s,"projector",colorSchemes)



def colorPicker():
    import tkColorChooser
    color = tkColorChooser.Chooser(
            initialcolor='gray',
            title="Choose background color").show()
            # color[0]: (r,g,b) tuple, color[1]: hex number
    master_widget.tk_setPalette(color[1]) # change bg color




if __name__ == '__main__':
    from Tkinter import *
    root = Tk()
    w=20
    h=20
    view = Canvas(root,width = 400, height = 400,bg='white')
    view.pack()

    devices = "desktop","projector","laptop","screen","paper"
    nColors = range(4,11)
    legendTypes = "qualitative","sequential","diverging"
    schemes = [ (lType,nC,dev) for lType in legendTypes for nC in \
                nColors for dev in devices ]

    # check out existing colorSchemes
    schemes = colorSchemes.getSchemes()
    for scheme in schemes:
        print scheme.key
        scheme.summary()
        nc = len(scheme.colors) 
        n = range(nc)
        rn = range(nc-1,-1,-1)
        view.create_text(5,7,text=scheme.key,tag=("cs"),anchor="w")
        for i in n:
            color = scheme.colors[i]
            rgb = scheme.rgb[i]
            view.create_rectangle(10+i*w,10+h,10+w+w*i,10+2*h,fill=color,tag=("cs"))
        for i in n:
            color = scheme.colors[i]
            rgb = scheme.rgb[i]
            view.create_rectangle(10+i*w,10+2*h,10+w+w*i,10+3*h,fill=color,tag=("cs"))
        for i in n:
            color = scheme.colors[rn[i]]
            rgb = scheme.rgb[rn[i]]
            view.create_rectangle(10+i*w,10+3*h,10+w+w*i,10+4*h,fill=color,tag=("cs"))
        for i in n:
            color = scheme.colors[rn[i]]
            rgb = scheme.rgb[rn[i]]
            view.create_rectangle(10+i*w,10+4*h,10+w+w*i,10+5*h,fill=color,tag=("cs"))
        raw_input("hit key to continue")
        view.delete("cs")


    root.mainloop()

    
    




