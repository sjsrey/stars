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


ax=fig.add_subplot(111)

minx=min(y1)
maxx=max(y1)
ax.axis([minx,maxx,minx,maxx])
ax.scatter(y1,wy1)
xlim((minx,maxx))
ylim((minx,maxx))
plt.xlabel('relative income 1969')
plt.ylabel('spatial lag of relative income 1969')

a=matplotlib.lines.Line2D([1,1],[minx,maxx],color='m') 
b=matplotlib.lines.Line2D([minx,maxx],[1,1],color='m') 
ax.add_line(a) 
ax.add_line(b)

plt.show()

