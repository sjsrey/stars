#!/usr/bin/env python

import numpy as np
import matplotlib.cm as cm
from matplotlib.pyplot import figure, show, rc
import pysal

def rose(u_theta,k=8):
    w=2*np.pi/k
    cuts=np.arange(0.0,2*np.pi+w,w)
    counts,bins=np.histogram(utheta,cuts)
    theta=np.arange(0.0,2*np.pi,2*np.pi/k)
    width=np.pi/(k/2.)
    fig = figure(figsize=(8,8))
    ax=fig.add_axes([0.1,0.1,0.8,0.8],polar=True)
    print len(theta),len(counts),
    bars=ax.bar(theta,counts,width=width,bottom=0.0)
    for r,bar in zip(counts,bars):
        bar.set_facecolor(cm.jet(r/10.))
        bar.set_alpha(0.5)
    show()

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

x=y2-y1
y=wy2-wy1
theta=np.arctan2(y,x)
neg=theta < 0.0
utheta=theta*(1-neg) + neg * (2*np.pi+theta)

rose(theta)


