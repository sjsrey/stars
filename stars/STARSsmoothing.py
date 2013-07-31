"""
Smoothing module for Space-Time Analysis of Regional Systems
----------------------------------------------------------------------
AUTHOR(S):  Sergio J. Rey sjrey@users.sourceforge.net
----------------------------------------------------------------------


OVERVIEW:

Contains various smoothing algorithms for STARS.


"""
from smoothing import *
from numpy.oldnumeric import *
class SWeight:
    """Facade class for STARS weights to work with PySAL Smoothing Class"""
    def __init__(self,w):
        neighbors = [ w.dict[i][1] for i in w.dict ]
        self.neighbors =neighbors

def rawRate(event, base):
    return event/base


class Smooth:
    """Wrapper to create smoothed rates"""
    def __init__(self, event, base, weight=None, method="RAW"):

        method=method.upper()
        self.rate=rawRate(event,base)
        n,k = shape(event)
        if rank(event) == 1:
            event = reshape(event,(n,1))
            base = reshape(base,(n,1))
            k=1
        rk = range(k)
        if method=="SPATIAL":
            if weight:
                smoothedRate = [SrSmoother(SWeight(weight),event[:,j],base[:,j])
                                     for j in rk ]
                self.smoothedRate = transpose(array(smoothedRate))
            else:
                print 'Weight objected needed for Smoothing'

        elif method=="RAW":
            self.smoothedRate = self.rate

        elif method=="BAYES":
            smoothedRate = [EbSmoother(event[:,j],base[:,j]) for j in rk ]
            self.smoothedRate = transpose(array(smoothedRate))
        else:
            print "Undefined Smoothing Method: ",method



if __name__ == '__main__':
    from smoothing import *
    from Markov import *

    p=Project("s")
    p.ReadProjectFile("data/geoda/nat.prj")

    w=p.getMatrix('nat_rook')
    hc = p.getVariable('HC')
    po = p.getVariable('PO')
    hc60 = hc[:,0]
    po60 = po[:,0]
    sw=SWeight(w)
    hrs60 = SrSmoother(sw,hc60,po60)



        

