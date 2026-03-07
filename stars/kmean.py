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


OVERVIEW:

This module implements the primitive graphics classes for STARS.


"""

import numpy as np


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
        n, k = data.shape
        self.n = n
        self.k = k
        self.scale()
        self.nClusters = clusters
        self.solve()

    def scale(self):
        """Standardize data matrix so variables have zero mean, unit variance.
        """
        xm = np.mean(self.data, axis=0)
        xd = self.data - xm
        xs = np.std(self.data, axis=0)
        z = xd / xs
        self.z = z

    def centroid(self, clusterMembers):
        """Calculate coordinates for centroid of a cluster.

        clusterMembers (list) integer ids of observations belonging to a
        cluster.

        RETURNS
        ct (Numeric Array) vector of centroid coordinates.
        """
        zc = np.take(self.z, clusterMembers, axis=0)
        try:
            ct = np.mean(zc, axis=0)
        except:
            print(clusterMembers)
            ct = zc
        return ct

    def distanceI2C(self, i, cent):
        """Observation distance to a centroid.

        i (integer) id for observation in data matrix.

        cent (Numeric Array) coordinates for centroid.

        RETURNS
        (float) Euclidean distance of observation to centroid.
        """

        zd = self.z[i, :] - cent
        zd = zd * zd
        return np.sqrt(np.sum(zd))

    def ss(self, cluster):
        """Sum of squares within a cluster.

        cluster (list) ids for observations in a cluster.

        RETURNS
        ss (float) sum of squares for cluster.
        """
        z = np.take(self.z, cluster, axis=0)
        mz = np.mean(z, axis=0)
        zd = z - mz
        ss = np.sum(zd * zd)
        return ss

    def wiss(self, clusters):
        """Calculates within cluster sum of squares for sets of clusters.

        clusters (list of lists) each element is a collection of integers for
        observation ids in cluster.

        RETURNS
        ss (float) total within sum of squares across clusters.
        """
        ss = [self.ss(cluster) for cluster in clusters]
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
            ids = np.random.randint(0, self.nClusters, self.n)
            k = list(dict(zip(ids, ids)).keys())
            if len(k) == self.nClusters:
                seedFlag = 0
        rc = range(self.nClusters)
        clusters = [np.nonzero(ids == i)[0] for i in rc]
        centroids = [self.centroid(cluster) for cluster in clusters]
        rn = range(self.n)
        flag = 1
        it = 0
        while flag:
            changed = np.zeros(self.n)
            for i in rn:
                dists = [self.distanceI2C(i, centroid) for centroid in centroids]
                minId = dists.index(min(dists))
                if minId != ids[i] and len(clusters[ids[i]]) > 1:
                    changed[i] = 1
                    oldId = ids[i]
                    newId = minId
                    oldCluster = clusters[oldId].tolist()
                    newCluster = clusters[newId].tolist()
                    oldCluster.remove(i)
                    newCluster.append(i)
                    old = np.array(oldCluster)
                    new = np.array(newCluster)
                    clusters[oldId] = old
                    clusters[newId] = new
                    ids[i] = newId
                    centroids[oldId] = self.centroid(old)
                    centroids[newId] = self.centroid(new)
            if np.sum(changed):
                it += 1
                print(it)
            else:
                flag = 0

        self.ids = ids
        self.centroids = centroids
        self.clusters = clusters
        self.iterations = it


if __name__ == '__main__':

    # a little demo
    import tkinter as Tk
    colors = {}
    colors[1] = "BLUE"
    colors[0] = "RED"
    colors[2] = "GREEN"
    colors[3] = "ORANGE"
    colors[4] = "PURPLE"
    root = Tk.Tk()
    can = Tk.Canvas(root, height=500, width=500, bg='white')
    can.grid()
    data = np.random.randint(100, 400, (1000, 2))
    points = []
    for point in data:
        xc, yc = point
        p = can.create_oval(xc - 2, yc - 2, xc + 2, yc + 2, fill='white')
        points.append(p)
    input('plot')
    nclusters = range(2, 6)
    for ncluster in nclusters:
        print(ncluster)
        km = Kmeans(data, ncluster)
        obs = zip(km.ids, data)
        for id, point in obs:
            x, y = point
            can.create_oval(x - 2, y - 2, x + 2, y + 2, fill=colors[id])

        input('Solution for %d clusters' % ncluster)

    root.mainloop()
