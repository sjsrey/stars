"""
Map views
"""

from stars.visualization.view import View
from pysal.esda.mapclassify import Quantiles, Percentiles, Std_Mean


__all__ = ['ChoroplethMap', 'mapClassifiers']

mapClassifiers = {'quantiles': Quantiles, 'percentiles': Percentiles, 'std':
        Std_Mean}


class Map(View):
    """Ancestor for all Maps"""
    def __init__(self):
        super(Map, self).__init__()


class ChoroplethMap(Map):
    def __init__(self, shapeFile, variable, classifier="quantiles"):
        super(ChoroplethMap, self).__init__()

    def __repr__(self):
        return self.name

