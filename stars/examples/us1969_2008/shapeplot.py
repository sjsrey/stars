
from mpl_toolkits.basemap import Basemap
# drawing
import matplotlib
#matplotlib.use('TkAgg')
import matplotlib.pyplot as P
from matplotlib import collections, axes, transforms
from matplotlib.colors import colorConverter
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
from matplotlib import colors as INK
from matplotlib import widgets as W
from matplotlib import nxutils as NX


BLUE=INK.colorConverter.to_rgba('blue')
GREEN=INK.colorConverter.to_rgba('green')
ORANGE=INK.colorConverter.to_rgba('orange')
COLORS=[BLUE,GREEN,ORANGE]


class ShapePlotter:
    """ """
    def __init__(self,shapefile,id_field):

        self.shapefile=shapefile
        self.id_field=id_field
        self.get_coords()
        self.plot()

    def get_coords(self):
        m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,\
            llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
        shp=Basemap.readshapefile(m,self.shapefile,name=self.id_field,\
                                  drawbounds=False)

        verts=m.__dict__[self.id_field]
        self.m=m
        self.verts=verts
        miny=minx=10**10
        maxy=maxx=-1*minx

        for poly in verts:
            poly=np.array(poly)
            mnx,mny=poly.min(axis=0)
            mxx,mxy=poly.max(axis=0)
            minx=min(minx,mnx)
            maxx=max(maxx,mxx)
            miny=min(miny,mny)
            maxy=max(maxy,mxy)


        low=np.array([minx,miny])
        high=np.array([maxx,maxy])
        rg=high-low

        sverts=[]
        for poly in verts:
                poly=np.array(poly)
                poly=(poly-(low))/rg
                sverts.append(poly)
        self.verts=sverts

    def plot(self):
        objects=[]
        self.xys=[]
        facecolors=[]
        for object in self.verts:
            self.xys.append(object.mean(axis=0))
            object=Polygon(object,True)
            objects.append(object)
            facecolors.append(GREEN)
        p=PatchCollection(objects,cmap=matplotlib.cm.jet,alpha=0.4, \
                          facecolors=facecolors)
        self.orig_colors=facecolors
        self.collection=p
        #p.set_array(np.array(colors))
        self.figure=P.figure()
        #P.get_current_fig_manager().window.wm_geometry(geometry)
        #P.get_current_fig_manager().window.wm_geometry("400x400+50+50")
        self.ax = self.figure.add_subplot(111)
        self.canvas=self.ax.figure.canvas
        self.cid=self.canvas.mpl_connect('button_press_event',self.onpress)
        self.lasso=W.RectangleSelector(self.ax, self.lineSelectCallback,
                                       drawtype='box',useblit=False,
                                       minspanx=5,minspany=5,
                                       spancoords='pixels')
        self.ax.add_collection(p)

    def lineSelectCallback(self, event1, event2):
        x1, y1 = event1.xdata, event1.ydata
        x2, y2 = event2.xdata, event2.ydata
        verts = ((x1,y1), (x2,y1), (x2,y2), (x1,y2), (x1,y1))
        ind = np.nonzero(NX.points_inside_poly(self.xys, verts))[0]
        print ind
        self.change_colors(ind)
        
    def onpress(self, event):
        if self.canvas.widgetlock.locked(): return
        if event.inaxes is None: return
        self.canvas.widgetlock(self.lasso)

    def change_colors(self, ids):
        facecolors=self.collection.get_facecolors()
        for i in range(len(facecolors)):
            if i in ids:
                print 'changing:', i
                facecolors[i]=INK.colorConverter.to_rgba('yellow')
            else:
                facecolors[i]=self.orig_colors[i]

        self.canvas.draw_idle()
        self.canvas.widgetlock.release(self.lasso)
        
    def randomize(self):
        facecolors=self.collection.get_facecolors()
        cids=np.random.randint(0,3,len(facecolors))
        col=[]
        for i in range(len(facecolors)):
            facecolors[i]=COLORS[cids[i]]
            col.append(facecolors[i])
        print 'rand'
        self.collection.set_facecolors(col)
        self.canvas.draw_idle()
        self.orig_colors=facecolors

if __name__ == '__main__':
    s=ShapePlotter('us48','State')
