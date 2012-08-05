#!/usr/bin/env python

import numpy as np
import matplotlib.cm as cm
from matplotlib.pyplot import figure, show, rc
import pysal

def draw(x,y,w,k):
    theta=np.arctan2(np.random.permutation(y),x)
    neg=theta < 0.0
    utheta=theta*(1-neg) + neg * (2*np.pi+theta)
    k=8
    width=2*np.pi/k
    cuts=np.arange(0.0,2*np.pi+width,width)
    counts,bin=np.histogram(utheta,cuts)
    return counts

def drawW(rel,w,k):
    r=np.random.permutation(rel)
    wy=pysal.lag_spatial(w,r)
    y=wy[:,-1]-wy[:,0]
    x=r[:,-1]-r[:,0]
    theta=np.arctan2(y,x)
    neg=theta < 0.0
    utheta=theta*(1-neg) + neg * (2*np.pi+theta)
    k=8
    width=2*np.pi/k
    cuts=np.arange(0.0,2*np.pi+width,width)
    counts,bin=np.histogram(utheta,cuts)
    return counts

def drawWcr(rel,w,k):
    wy=np.zeros((w.n,1),'Float')
    ids=arange(w.n)
    for i in range(w.n):
        ni= w.cardinalities[i]
        rids=np.random.permutation(ids[ids!=i])[0:ni]
        wy[i,0]=w.weights[i]*rel[rids]
    y=wy[:,-1]-wy[:,0] 

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

def prose(z):
    k=len(z)
    theta=np.arange(0.0,2*np.pi,2*np.pi/k)
    width=np.pi/(k/2.)
    fig = figure(figsize=(8,8))
    ax=fig.add_axes([0.1,0.1,0.8,0.8],polar=True)
    counts=np.ones(k)
    bars=ax.bar(theta,counts,width=width,bottom=0.0)
    i=0
    for r,bar in zip(counts,bars):
        color='white'
        if z[i]>1.96:
            color='red'
        elif z[i]<-1.96:
            color='blue'
        bar.set_facecolor(color)
        bar.set_alpha(0.5)
        i+=1
    #show()

    fig.savefig('prose_82.png',dpi=600)



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
k=8
width=2*np.pi/k
cuts=np.arange(0.0,2*np.pi+width,width)
counts,bin=np.histogram(utheta,cuts)

np.random.seed(10)
nperm=999
simc=np.array([drawW(rel,w,8) for i in range(nperm)])
z=(counts-simc.mean(axis=0))/simc.std(axis=0)

# directional pvalues
pg=np.array([(sum(simc[:,i]>=counts[i])+1.)/(nperm+1) for i in range(k)])
pl=np.array([(sum(simc[:,i]<=counts[i])+1.)/(nperm+1) for i in range(k)])


from pylab import *
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib
from scipy import stats

mu, sigma = 100, 15
x = simc[:,1]*1. #cast to float
mu = np.mean(x)
sigma=np.std(x)

ind=np.linspace(0,20,101)
gkde=stats.gaussian_kde(x)
kde=gkde.evaluate(ind)

fig=plt.figure()
ax=fig.add_subplot(111)

ax.plot(ind,kde)


plt.xlabel('Count')
plt.ylabel('P(x)')
plt.title(r'$\mathrm{Kenel\ Density\ of\ Counts\ in\ Segment\ 2}\ \mu=9.14,\ \sigma=1.94$')
plt.grid(True)

a=matplotlib.lines.Line2D([13,13],[0.0,0.25])
ax.add_line(a)

#plt.show()
plt.savefig('kde2.png',dpi=600)

xm=np.mean(simc,axis=0)
xs=np.std(simc,axis=0)
z=(counts-xm)/xs

pz=1-stats.norm.cdf(abs(z))
tab=np.transpose(np.vstack((z,pz)))

counts.shape=(8,1)
xm.shape=(8,1)
xs.shape=(8,1)
tab=np.hstack((counts,xm,xs,tab))

prose(z)
