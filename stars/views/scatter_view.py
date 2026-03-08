"""Scatter-plot view for STARS (Phase 2c).

Replaces gView.CScatterPlot (tkinter canvas ovals coloured by a third
variable z) with a matplotlib scatter coloured by z.

Public interface (mirrors gView.CScatterPlot):
  ScatterView(name, observer, x, y, varName,
              csIds, z, zLabel, nColors,
              xLabel, yLabel, time_string)
"""

import sys
import os
import numpy as np

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from views.base import STARSView

_HIGHLIGHT_COLOR = 'gold'


class ScatterView(STARSView):
    """Scatter-plot window backed by matplotlib.

    Parameters
    ----------
    name : str
        Window title.
    observer : Observer
        STARS viewObserver singleton.
    x : array-like, shape (n_cs,)
        Horizontal axis values.
    y : array-like, shape (n_cs,)
        Vertical axis values.
    varName : str
        Primary variable name (used in title).
    csIds : list
        Cross-sectional ids corresponding to observations.
    z : array-like or None, shape (n_cs,)
        Optional third variable that controls dot colour.
    zLabel : str
        Label for z (shown in legend/colorbar).
    nColors : int
        Number of colour classes for z (default 6).
    xLabel : str
        X-axis label.
    yLabel : str
        Y-axis label.
    time_string : str
        Human-readable time label appended to title.
    """

    _nsc = 0

    def __init__(self, name, observer,
                 x, y, varName,
                 csIds=None, z=None, zLabel='Z', nColors=6,
                 xLabel='X', yLabel='Y',
                 time_string='', width=None, height=None):

        ScatterView._nsc += 1
        view_name = f'scatter_{ScatterView._nsc}'
        title = f'{name}  {time_string}' if time_string else name

        self.varName = varName
        self._x = np.asarray(x, dtype=float)
        self._y = np.asarray(y, dtype=float)
        n = len(self._x)
        self._csIds = list(csIds) if csIds is not None else list(range(n))
        self._z = np.asarray(z, dtype=float) if z is not None else None
        self.zLabel = zLabel
        self.nColors = nColors
        self.xLabel = xLabel
        self.yLabel = yLabel

        # cs_id → (x, y) for hit-testing
        self._cs_to_xy = {cs: (float(self._x[i]), float(self._y[i]))
                          for i, cs in enumerate(self._csIds)}
        self._selected_scatter = None

        super().__init__(view_name, 'cscatter', observer,
                         width=width, height=height, title=title)

    # ── Drawing ───────────────────────────────────────────────────────────

    def draw(self):
        """Render the scatter plot, coloured by z if provided."""
        self.ax.clear()
        self._selected_scatter = None

        if self._z is not None:
            sc = self.ax.scatter(self._x, self._y, c=self._z,
                                 cmap='RdYlBu_r', s=18, linewidths=0.3,
                                 edgecolors='black', alpha=0.8)
            self.fig.colorbar(sc, ax=self.ax, label=self.zLabel, shrink=0.8)
            self.ax.set_title(f'{self.varName}  (conditioned on {self.zLabel})',
                              fontsize=9)
        else:
            self.ax.scatter(self._x, self._y, s=18, color='#4c72b0',
                            linewidths=0.3, edgecolors='black', alpha=0.8)
            self.ax.set_title(self.varName, fontsize=9)

        # OLS regression line
        if len(self._x) > 1:
            m, b = np.polyfit(self._x, self._y, 1)
            xfit = np.array([self._x.min(), self._x.max()])
            self.ax.plot(xfit, m * xfit + b, color='black',
                         linewidth=0.8, linestyle='--', alpha=0.6)

        self.ax.set_xlabel(self.xLabel, fontsize=8)
        self.ax.set_ylabel(self.yLabel, fontsize=8)
        self.ax.tick_params(labelsize=7)

    # ── Hit-testing ───────────────────────────────────────────────────────

    def _hit_test(self, x0, y0, x1, y1):
        """Return cs_ids whose (x, y) fall within the selection rectangle."""
        xmin, xmax = min(x0, x1), max(x0, x1)
        ymin, ymax = min(y0, y1), max(y0, y1)
        return [cs for cs, (cx, cy) in self._cs_to_xy.items()
                if xmin <= cx <= xmax and ymin <= cy <= ymax]

    # ── Highlighting ──────────────────────────────────────────────────────

    def highlightObservations(self, cs_ids):
        """Overlay selected points as large yellow markers."""
        if self._selected_scatter is not None:
            try:
                self._selected_scatter.remove()
            except ValueError:
                pass
            self._selected_scatter = None

        if not cs_ids:
            return

        cs_set = set(cs_ids)
        pts = [(cx, cy) for cs, (cx, cy) in self._cs_to_xy.items()
               if cs in cs_set]
        if not pts:
            return
        xs, ys = zip(*pts)
        self._selected_scatter = self.ax.scatter(
            xs, ys, color=_HIGHLIGHT_COLOR,
            edgecolors='black', linewidths=0.5,
            s=40, zorder=5)

    def unhighlightObservations(self, cs_ids):
        if self._selected_scatter is not None:
            try:
                self._selected_scatter.remove()
            except ValueError:
                pass
            self._selected_scatter = None
            self.canvas.draw_idle()

    # ── Subscriber overrides ───────────────────────────────────────────────

    def selectedObservations(self, obs_ids):
        """cscatter must publish 'newSelectedObservations' for Interaction.py routing."""
        self.selectObservations(obs_ids)
        self.publish('newSelectedObservations', obs_ids)

    def buildMethods(self):
        super().buildMethods()
        self.methods.update({
            'newSelectObservations': self.selectObservations,
            'selectObservationsCS':  self.selectObservations,
        })

    # ── Time update ───────────────────────────────────────────────────────

    def updateTime(self, ts_id):
        """Switch to a new time period (requires _x_full, _y_full arrays)."""
        if isinstance(ts_id, (list, tuple)):
            ts_id = ts_id[0]
        changed = False
        if hasattr(self, '_x_full') and self._x_full.ndim == 2:
            self._x = self._x_full[:, ts_id]
            changed = True
        if hasattr(self, '_y_full') and self._y_full.ndim == 2:
            self._y = self._y_full[:, ts_id]
            changed = True
        if changed:
            self._cs_to_xy = {cs: (float(self._x[i]), float(self._y[i]))
                              for i, cs in enumerate(self._csIds)}
            self.draw()
            self.canvas.draw_idle()
