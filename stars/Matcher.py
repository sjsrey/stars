"""  Matcher.py

Matcher module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Mark V. Janikas mjanikas@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

This module contains several generic matching utilities at the top.
The Matcher Class is used for a single vector with multiple
instances of the same value occuring through the list.
"""

import sets

def createBridge(list1,list2):
    "Returns an index list for mapping list2 values into list1 order."
    return [ list1.index(i) for i in list2 ] 

def mapValues(bridge,list):
    """Maps based on a bridge.
    bridge indexes place in return list
    list are the values returned in new order."""
    return [ list[i] for i in bridge ] 

def batchSplit(list):
    null = []
    strings = []
    ints = []
    suff = []
    for string in list:
        if string.isalpha():
            null.append(string)
            #print "No numeric argument to batch with"
        else:
            sp = [ i.isalpha() for i in string ]
            spi = sp.index(False)
            if string[spi].isalnum():
                strings.append(string[0:spi])
                suff.append(string[spi:])
                if string[spi:].isalnum():
                    ints.append(string[spi:])
            else:
                #print "No numeric argument to batch with"
                null.append(string)
    return {'strings':uniqueList(strings), 'ints':uniqueList(ints),
            'null':null, 'allSuffix':uniqueList(suff)}
    

def uniqueList(l):
    s = sets.Set(l)
    s = list(s)
    return s

class Matcher:
    """Agg Scheme Class
    """
    def __init__(self,name,vector):
        self.name = name
        self.vector = vector
        self.createScheme()

    def createScheme(self):
        self.unique = []
        self.matched = []
        self.scheme2Master = {}
        self.master2Scheme = {}
        u = 0
        for row in range(len(self.vector)):
            value = self.vector[row]
            if value not in self.unique:
                self.unique.append(value)
                self.scheme2Master[u] = [row]
                self.master2Scheme[row] = u
                u = u+1
            else:
                ind = self.unique.index(value)
                self.scheme2Master[ind].append(row)
                self.master2Scheme[row] = ind
            self.matched.append(self.master2Scheme[row])

    def returnValue(self,ind):
        return self.master2Scheme[self.unique[ind]]

        
if __name__ == '__main__':
    a = ['dog','cat','cat','bird','bird','dog','cat']
    agg = Matcher('animals',a)
    agg.createScheme()

    b = ['hat', 'shoes', 'shoes', 'shoes', 'hat', 'shoes', 'shoes']
    agg1 = Matcher('clothes',b)
    agg1.createScheme()

    # same length for join method

    x = ["a", "b", "c", "d"]
    y = ["b", "a", "d", "c"]
    z = [ ['test', 'this'], ['test', 'that'], ['and', 'this'], ['or', 'that'] ]
    agg2 = Matcher("join", x)
    b = createBridge(x,y)
    map = mapValues(b,y)
    map2 = mapValues(b,z)

    new = ["a1", "a2", "a3", "b", "c1", "c2", "c3", "c4"]
    b = batchSplit(new)
