import pysal
import numpy as np

f=open("spi_download.csv",'r')
lines=f.readlines()
f.close()

lines=[line.strip().split(",") for line in lines]
names=[line[2] for line in lines[1:-5]]
data=np.array([map(int,line[3:]) for line in lines[1:-5]])
sids=range(60)
out=['"United States 3/"','"Alaska 3/"',
     '"District of Columbia"',
     '"Hawaii 3/"',
     '"New England"',
 '"Mideast"',
 '"Great Lakes"',
 '"Plains"',
 '"Southeast"',
 '"Southwest"',
 '"Rocky Mountain"',
 '"Far West 3/"']
snames=[name for name in names if name not in out]
sids=[names.index(name) for name in snames]
states=data[sids,:]
us=data[0]

from pylab import *

years=np.arange(1969,2009)
rel=states/(us*1.)

gal=pysal.open('states48.gal')
w=gal.read()
rt=rel.transpose()
w.transform='r'
wrel=pysal.lag_spatial(w,rel)

y1=rel[:,0]
wy1=wrel[:,0]
y2=rel[:,-1]
wy2=wrel[:,-1]


minx,miny=rel.min(),rel.min()
maxx,maxy=rel.max(),rel.max()
import matplotlib.pyplot as plt
import matplotlib.patches as mpp
fig=plt.figure()

dx=y2-y1
dy=wy2-wy1

ax=fig.add_subplot(111)

minx=min(dx)
maxx=max(dx)
ax.axis([minx,maxx,minx,maxx])

for i in range(48):
    p2=(dx[i],dy[i])
    p1=(0,0)
    c = mpp.FancyArrowPatch(p1, p2, arrowstyle='-|>', lw=1, mutation_scale=20)
    ax.add_patch(c)
plt.show()



"""
plot(y1,wy1)
plot(y2,wy2)
arr=Arrow(y1[0],wy1[0],y2[0],wy2[0],width=0.10,edgecolor='white')
ax=gca()
ax.add_patch(arr)
arr.set_facecolor('g')
scatter(y1,wy1)

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

# the random data
x = y1
y = wy1

nullfmt   = NullFormatter()         # no labels

# definitions for the axes
left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
bottom_h = left_h = left+width+0.02

rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom_h, width, 0.2]
rect_histy = [left_h, bottom, 0.2, height]

# start with a rectangular Figure
plt.figure(1, figsize=(8,8))

axScatter = plt.axes(rect_scatter)
axHistx = plt.axes(rect_histx)
axHisty = plt.axes(rect_histy)

# no labels
axHistx.xaxis.set_major_formatter(nullfmt)
axHisty.yaxis.set_major_formatter(nullfmt)

# the scatter plot:
axScatter.scatter(x, y)

# now determine nice limits by hand:
binwidth = 0.05
xymax = np.max( [np.max(np.fabs(x)), np.max(np.fabs(y))] )
lim = ( int(xymax/binwidth) + 1) * binwidth

axScatter.set_xlim( (-lim, lim) )
axScatter.set_ylim( (-lim, lim) )

bins = np.arange(-lim, lim + binwidth, binwidth)
axHistx.hist(x, bins=bins)
axHisty.hist(y, bins=bins, orientation='horizontal')

axHistx.set_xlim( axScatter.get_xlim() )
axHisty.set_ylim( axScatter.get_ylim() )

plt.show()
"""
