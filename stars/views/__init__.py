"""PyQt6 + matplotlib view package for STARS (Phase 2).

Provides framework-independent STARSView base class and concrete view
implementations that replace the tkinter Canvas-based gView.py views.

The Observer/Subscriber wiring (Subscriber.py, Interaction.py) is unchanged;
only the rendering backend switches from tkinter.Canvas to FigureCanvasQTAgg.
"""
from .base import STARSView
from .map_view import MapView
from .histogram_view import HistogramView
from .timeseries_view import TimeSeriesView
from .boxplot_view import BoxPlotView
from .cdf_view import CDFView
from .scatter_view import ScatterView
from .pcp_view import PCPView
from .table_view import TableView
from .moran_scatter_view import MoranScatterView

__all__ = [
    'STARSView', 'MapView', 'HistogramView',
    'TimeSeriesView', 'BoxPlotView', 'CDFView', 'ScatterView', 'PCPView',
    'TableView', 'MoranScatterView',
]
