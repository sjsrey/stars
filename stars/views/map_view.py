"""Choropleth map view for STARS (Phase 2c).

Replaces gView.Map (tkinter canvas.create_polygon loop) with:
  - geopandas GeoDataFrame from STARS polygon coords
  - gdf.plot() for classification-based color fill
  - gdf.sindex.query() for spatial hit-testing (selection / brushing)
  - matplotlib rubber-band via base.STARSView

Public interface (mirrors gView.Map):
  MapView(name, observer, coords, values, varName, t,
          poly2cs, cs2poly, classification, nBins, bins, legendType)
"""

import sys
import os
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, Point, box as shapely_box
from matplotlib.patches import Patch
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import matplotlib.colors as mcolors
import matplotlib.cm as cm

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from views.base import STARSView
import classifier as _clf
import color as _color


# ── Colour palettes (mirrors gView.getColors) ──────────────────────────────

_SEQUENTIAL = [
    '#ffffcc', '#c7e9b4', '#7fcdbb', '#41b6c4', '#1d91c0',
    '#225ea8', '#0c2c84',
]
_DIVERGING = [
    '#d73027', '#f46d43', '#fdae61', '#fee090',
    '#e0f3f8', '#abd9e9', '#74add1', '#4575b4',
]
_QUALITATIVE = [
    '#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
    '#ff7f00', '#a65628', '#f781bf', '#999999',
]


def _palette(legend_type, n):
    """Return a list of n hex colour strings for the given legend_type."""
    if legend_type == 'sequential':
        base = _SEQUENTIAL
    elif legend_type == 'diverging':
        base = _DIVERGING
    else:
        base = _QUALITATIVE
    # Subsample or cycle to get exactly n colours
    indices = np.linspace(0, len(base) - 1, n, dtype=int)
    return [base[i] for i in indices]


def _flat_to_polygon(coords_flat):
    """Convert STARS flat [x0,y0,x1,y1,...] list to a shapely Polygon."""
    xi = range(0, len(coords_flat), 2)
    pts = [(coords_flat[i], coords_flat[i + 1]) for i in xi]
    if len(pts) < 3:
        return None
    return Polygon(pts)


class MapView(STARSView):
    """Choropleth map window backed by geopandas + matplotlib.

    Parameters
    ----------
    name : str
        Window title / view name.
    observer : Observer
        STARS viewObserver singleton.
    coords : dict
        {polyId: [x0, y0, x1, y1, ...]} — STARS polygon vertex list.
    values : array-like, shape (n_cs,)
        Scalar value per cross-sectional unit.
    varName : str
        Variable name shown in title and legend.
    t : int
        Time period index (for title).
    poly2cs : dict
        {polyId: [csId, ...]}
    cs2poly : dict
        {csId: [polyId, ...]}
    classification : str
        Classifier method ('percentiles', 'equalWidth', 'equalCount', ...).
    nBins : int
        Number of classification bins.
    bins : list
        Pre-specified bin edges (empty list = compute from data).
    legendType : str
        'sequential', 'diverging', or 'qualitative'.
    time_string : str
        Human-readable time label (appended to title).
    """

    _nmap = 0

    def __init__(self, name, observer,
                 coords, values, varName, t,
                 poly2cs, cs2poly,
                 classification='percentiles',
                 nBins=5, bins=None, legendType='sequential',
                 time_string='', width=None, height=None):

        MapView._nmap += 1
        view_name = f'map_{MapView._nmap}'
        title = f'{name}  {time_string}' if time_string else name

        # Store data before super().__init__ calls draw()
        self.coords = coords
        self.values = np.asarray(values, dtype=float)
        self.varName = varName
        self.t = t
        self.poly2cs = poly2cs
        self.cs2poly = cs2poly
        self.classification = classification
        self.nBins = nBins
        self._bins_input = bins or []
        self.legendType = legendType

        # Build GeoDataFrame once
        self._gdf, self._poly_to_cs = self._build_gdf()
        # Classify values → bin ids per cs unit
        self._classify()

        super().__init__(view_name, 'map', observer,
                         width=width, height=height, title=title)

    # ── GeoDataFrame construction ─────────────────────────────────────────

    def _build_gdf(self):
        """Convert STARS coords dict to a GeoDataFrame with one row per polygon."""
        geoms, poly_ids, cs_ids = [], [], []
        for pid, flat in self.coords.items():
            poly = _flat_to_polygon(flat)
            if poly is None or not poly.is_valid:
                poly = poly.buffer(0) if poly else None
            if poly is None:
                continue
            cs = self.poly2cs[pid][0]  # primary cs unit
            geoms.append(poly)
            poly_ids.append(pid)
            cs_ids.append(cs)

        gdf = gpd.GeoDataFrame(
            {'poly_id': poly_ids, 'cs_id': cs_ids},
            geometry=geoms,
            crs=None,
        )
        gdf = gdf.set_index('poly_id')
        # Spatial index built automatically by geopandas
        poly_to_cs = {pid: cs for pid, cs in zip(poly_ids, cs_ids)}
        return gdf, poly_to_cs

    def _classify(self):
        """Run the STARS classifier and assign colours to each polygon."""
        x = self.values
        clf = _clf.Classifier(x, method=self.classification, nBins=self.nBins,
                              bins=self._bins_input)
        self._bin_ids = clf.binIds          # (n_cs,) array of bin indices
        self._bins = clf.bins               # list of bin edge values
        n_bins = len(self._bins)
        self._colors = _palette(self.legendType, n_bins)

        # Map each polygon → fill colour via cs_id → bin_id → colour
        cs_to_color = {
            cs: self._colors[min(self._bin_ids[cs], n_bins - 1)]
            for cs in range(len(self.values))
        }
        self._gdf['color'] = [
            cs_to_color.get(cs, '#888888')
            for cs in self._gdf['cs_id']
        ]
        self._cs_to_color = cs_to_color

    # ── Drawing ───────────────────────────────────────────────────────────

    def draw(self):
        """Render the choropleth map."""
        self.ax.clear()
        self._gdf.plot(ax=self.ax, color=self._gdf['color'],
                       edgecolor='black', linewidth=0.3)
        self.ax.set_aspect('equal')
        self.ax.invert_yaxis()
        self.ax.axis('off')
        self.ax.set_title(f'{self.varName}', fontsize=9, pad=4)
        self._draw_legend()

    def _draw_legend(self):
        """Draw a simple categorical legend."""
        n = len(self._bins)
        handles = []
        for i, (c, b) in enumerate(zip(self._colors, self._bins)):
            if i == 0:
                lbl = f'≤ {b:.2f}'
            else:
                lbl = f'{self._bins[i-1]:.2f} – {b:.2f}'
            handles.append(Patch(facecolor=c, edgecolor='black',
                                 linewidth=0.5, label=lbl))
        self.ax.legend(handles=handles, loc='lower right',
                       fontsize=7, framealpha=0.8,
                       title=self.varName, title_fontsize=7)

    # ── Selection / brushing ──────────────────────────────────────────────

    def buildMethods(self):
        super().buildMethods()
        self.methods.update({
            'selectPolygons':        self.selectPolygons,
            'selectedPolygons':      self.selectedPolygons,
            'brushPolygons':         self.brushPolygons,
            'newSelectObservations': self.highlightObservations,
            'selectObservationsCS':  self.highlightObservations,
        })

    def selectedObservations(self, obs_ids):
        """map publishes both commands so all view types respond."""
        self.selectObservations(obs_ids)
        self.publish('selectedObservations', obs_ids)
        self.publish('newSelectedObservations', obs_ids)

    def _hit_test(self, x0, y0, x1, y1):
        """Return list of cs_ids whose polygons overlap the selection box."""
        sel_box = shapely_box(min(x0, x1), min(y0, y1),
                              max(x0, x1), max(y0, y1))
        # Use spatial index for fast query
        candidates = list(self._gdf.sindex.query(sel_box, predicate='intersects'))
        if not candidates:
            return []
        hit_polys = self._gdf.iloc[candidates]
        cs_ids = list(hit_polys['cs_id'].unique())
        return cs_ids

    def selectPolygons(self, poly_ids):
        """Highlight the given polygon ids (called by observer dispatch)."""
        # Convert poly_ids to cs_ids
        cs_ids = set()
        for pid in poly_ids:
            cs_ids.update(self.poly2cs.get(pid, []))
        self.highlightObservations(list(cs_ids))
        self.canvas.draw_idle()

    def selectedPolygons(self, poly_ids):
        self.selectPolygons(poly_ids)
        self.publish('selectedPolygons', poly_ids)

    def brushPolygons(self, poly_ids):
        self.selectPolygons(poly_ids)

    def highlightObservations(self, cs_ids):
        """Overlay yellow borders on polygons matching cs_ids."""
        for artist in getattr(self, '_highlight_artists', []):
            try:
                artist.remove()
            except ValueError:
                pass
        self._highlight_artists = []
        self.selectedIds = set(cs_ids)

        if not cs_ids:
            self.canvas.draw_idle()
            return

        cs_set = set(cs_ids)
        mask = self._gdf['cs_id'].isin(list(cs_set))
        highlighted = self._gdf[mask]
        if highlighted.empty:
            self.canvas.draw_idle()
            return

        patches = []
        for geom in highlighted.geometry:
            if geom is None:
                continue
            if geom.geom_type == 'Polygon':
                patches.append(MplPolygon(np.array(geom.exterior.coords), closed=True))
            elif geom.geom_type == 'MultiPolygon':
                for part in geom.geoms:
                    patches.append(MplPolygon(np.array(part.exterior.coords), closed=True))

        if patches:
            pc = PatchCollection(patches, facecolor='none', edgecolor='yellow',
                                 linewidth=2, zorder=5)
            self.ax.add_collection(pc)
            self._highlight_artists = [pc]
        self.canvas.draw_idle()

    def unhighlightObservations(self, cs_ids):
        for artist in getattr(self, '_highlight_artists', []):
            artist.remove()
        self._highlight_artists = []

    # ── Time update ───────────────────────────────────────────────────────

    def updateTime(self, ts_id):
        """Switch to a new time period (re-classify and redraw)."""
        if isinstance(ts_id, (list, tuple)):
            ts_id = ts_id[0]
        # If values is 2D (n×t), slice to new time period
        if hasattr(self, '_values_full') and self._values_full.ndim == 2:
            self.values = self._values_full[:, ts_id]
            self._classify()
            self.draw()
            self.canvas.draw_idle()
