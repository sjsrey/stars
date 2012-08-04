"""
Map views
"""

from stars.visualization.view import View


__all__ = ['ChoroplethMap']


class Map(View):
    """Ancestor for all Maps"""
    def __init__(self):
        View.__init__(self)
        self.name = 'Map'


class ChoroplethMap(Map):
    def __init__(self):
        Map.__init__(self)
        self.name='Choropleth'


