from mpl_toolkits.basemap import Basemap
m = Basemap(projection='merc',llcrnrlat=-80,urcrnrlat=80,\
            llcrnrlon=-180,urcrnrlon=180,lat_ts=20,resolution='c')
shp=Basemap.readshapefile(m,'us48',name='State',drawbounds=False)
verts=m.State


# drawing
import matplotlib.pyplot as P
from matplotlib import collections, axes, transforms
from matplotlib.colors import colorConverter
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib
import numpy as np
from matplotlib import colors as INK
from matplotlib import widgets as W
from matplotlib import nxutils as NX


fig=P.figure()
ax=fig.add_subplot(111)
canvas=ax.figure.canvas
patches=[]
f=1
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

for poly in verts:
        poly=np.array(poly)
        poly=(poly-(low))/rg
        polygon=Polygon(poly,True)
        patches.append(polygon)
p=PatchCollection(patches,cmap=matplotlib.cm.jet,alpha=0.4)
colors=100*np.random.rand(len(patches))
p.set_array(np.array(colors))
ax.add_collection(p)
P.show()

