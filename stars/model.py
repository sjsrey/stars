"""
model module for stars

model-view-controller
"""

import pandas as pd


class Variable:
    """ """
    def __init__(self, data):
        self.set_data(data)

    def set_data(self,data):
        """integration of pandas"""
        self.data = pd.DataFrame(data)

    def transform(self, **args):
        pass

    def aggregate(self, **args):
        pass

    def slice(self, **args):
        pass


    def interpolate(self, **args):
        pass

    def extrapolate(self, **args):
        pass

    def to_array(self):
        return self.data.as_matrix()

    def time_difference(self,k=1):
        v = self.data - self.data.T.shift(k).T
        return Variable(v.as_matrix())


    def slice(self, **args):
        """handle slicing interface to pandas"""
        for key in args:
            print key, args[key]



if __name__ == '__main__':

    n,t = (5,4)
    import numpy as np
    x = np.arange(n*t)
    x.shape=(n,t)
    v = Variable(x)

