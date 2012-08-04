"""
Abstract class for all stars views
"""

class View(object):
    """
    Abstract View for all stars interactive views

    Core visualization, interaction, animation is defined in this class

    Specialized functionality is implemented in descendants.
    
    """
    def __init__(self):
        self.name = 'view'
        self.selectedWidgets = []
        self.widgets = []

    def __repr___(self):
        return  self.name

    def summary(self):
        print 'View summary'

    def highlightWidgets(self, widgets=[]):
        pass

    def unHighlightWidgets(self, widgets=[]):
        pass

    def plot(self):
        pass

    def save(self, fileName):
        pass
