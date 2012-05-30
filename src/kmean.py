#!/usr/local/bin/python
#
# kmeans.py
#
# ----------------------------------------------------------------------
# kmeans clustering

"""
kmeans clustering module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------
Copyright (c) 2000-2006  Sergio J. Rey
======================================================================
This source code is licensed under the GNU General Public License, 
Version 2.  See the file COPYING for more details.
======================================================================

OVERVIEW:

This module implements the primitive graphics classes for STARS.


"""

from numpy.oldnumeric import *
from numpy.oldnumeric.random_array import *


class Kmeans:
    """Kmeans clustering of a set of vectors.
    
    Assumes observations are on rows, variables on columns"""
    def __init__(self, data, clusters=2):
        """
        data (Numeric array) n rows=observations, k cols=variables. clustering
        is done across rows (i.e., observations).

        clusters (integer) number of clusters to be formeed.
        """

        self.data = data
        n,k = shape(data)
        self.n = n
        self.k = k
        self.scale()
        self.nClusters = clusters
        self.solve()

    def scale(self):
        """Standardize data matrix so variables have zero mean, unit variance.
        """
        xm = mean(self.data)
        xd = self.data - xm
        xs = self.data.std()
        z = xd/xs
        self.z = z

    def centroid(self,clusterMembers):
        """Calculate coordinates for centroid of a cluster.

        clusterMembers (list) integer ids of observations belonging to a
        cluster.

        RETURNS
        ct (Numeric Array) vector of centroid coordinates.
        """
        zc = take(self.z,clusterMembers)
        try:
            ct = mean(zc)
        except:
            print clusterMembers
            ct = zc
        return ct

    def distanceI2C(self,i,cent):
        """Observation distance to a centroid.

        i (integer) id for observation in data matrix.

        cent (Numeric Array) coordinates for centroid.

        RETURNS
        (float) Euclidean distance of observation to centroid.
        """

        zd = self.z[i,:] - cent
        zd = zd*zd
        return sqrt(sum(sum(zd)))


    def ss(self,cluster):
        """Sum of squares within a cluster.

        cluster (list) ids for observations in a cluster.

        RETURNS
        ss (float) sum of squares for cluster.
        """
        z = take(self.z,cluster)
        mz = mean(z)
        zd=z-mz
        ss=sum(sum(zd*zd))
        return ss

    def wiss(self,clusters):
        """Calculates within cluster sum of squares for sets of clusters.

        clusters (list of lists) each element is a collection of integers for
        observation ids in cluster.

        RETURNS
        ss (float) total within sum of squares across clusters.
        """
        ss = [ self.ss(cluster) for cluster in clusters ] 
        return sum(ss)

    def solve(self):
        """Wrapper method to implement kmeans agorithm.

        RETURNS
            None
        
        ATTRIBUTES
            ids (list) integer ids for cluster membership.

            centroids (dictionary) centroids for each cluster, key is cluster
            id, values are centroids.

            clusters (dictionary) keys are cluster ids, values are lists of
            observation ids

            iterations (int) number of iterations needed for solution.
        """
        seedFlag = 1
        while seedFlag:
            ids = randint(0,self.nClusters,self.n)
            k = dict(zip(ids,ids)).keys()
            if len(k) == self.nClusters:
                seedFlag=0
        rc = range(self.nClusters)
        clusters = [ nonzero(ids==i) for i in rc ]
        centroids = [ self.centroid(cluster) for cluster in clusters ]
        rn = range(self.n)
        flag = 1
        it = 0
        while flag:
            #print self.wiss(clusters)
            #print ids
            changed = zeros(self.n)
            for i in rn:
                dists = [self.distanceI2C(i,centroid) for centroid in centroids]
                minId = dists.index(min(dists))
                if minId != ids[i] and len(clusters[ids[i]]) > 1:
                    changed[i] = 1
                    oldId = ids[i]
                    newId = minId
                    oldCluster = clusters[oldId].tolist()
                    newCluster = clusters[newId].tolist()
            #        print oldCluster,newCluster,i
                    oldCluster.remove(i)
                    newCluster.append(i)
            #        print oldCluster,newCluster,i
                    old = array(oldCluster)
                    new = array(newCluster)
                    clusters[oldId] = old
                    clusters[newId] = new
                    ids[i] = newId
                    centroids[oldId] = self.centroid(old)
                    centroids[newId] = self.centroid(new)
            #        raw_input('wait')
            if sum(changed):
                it +=1
                print it
            else:
                flag = 0


        self.ids = ids
        self.centroids = centroids
        self.clusters = clusters
        self.iterations = it








if __name__ == '__main__':

    # a little demo
    from Tkinter import *
    colors ={}
    colors[1] = "BLUE"
    colors[0] = "RED"
    colors[2] = "GREEN"
    colors[3] = "ORANGE"
    colors[4] = "PURPLE"
    root = Tk()
    can = Canvas(root,height=500,width=500,bg='white')
    can.grid()
    data=randint(100,400,(1000,2))
    points = []
    for point in data:
        xc,yc = point
        p=can.create_oval(xc-2,yc-2,xc+2,yc+2,fill='white')
        points.append(p)
    raw_input('plot')
    nclusters = range(2,6)
    for ncluster in nclusters:
        print ncluster
        km = Kmeans(data, ncluster)
        obs = zip(km.ids, data)
        for id,point in obs:
            x,y = point
            can.create_oval(x-2,y-2,x+2,y+2,fill=colors[id])

        raw_input('Solution for %d clusters'%ncluster)



    root.mainloop()
