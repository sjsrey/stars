"""Moran scatter plot view for STARS (Phase 2c).

Replaces gView.MoranScatter (tkinter canvas) with matplotlib.
Shows standardised variable (x) vs spatial lag (y), with:
  - Cross-hair at (mean_x, mean_lag) dividing HH/LH/LL/HL quadrants
  - OLS regression line (slope = Moran's I)
  - Optional LISA quadrant colouring from LocalMoran results
  - Same rectangle hit-test and yellow highlight as ScatterView

Public interface:
  MoranScatterView(name, observer, x, y_lag, varName, t,
                   csIds, quad_ids, sig_mask, time_string)
"""

import sys
import os
import numpy as np

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from views.base import STARSView

# LISA quadrant colours: 0=not significant, 1=HH, 2=LH, 3=LL, 4=HL
_QUAD_COLORS = {
    0: '#aaaaaa',   # not significant / no quad info
    1: '#d7191c',   # HH — red
    2: '#fdae61',   # LH — orange
    3: '#2c7bb6',   # LL — blue
    4: '#abd9e9',   # HL — light blue
}
_HIGHLIGHT_COLOR = 'gold'


class MoranScatterView(STARSView):
    """Moran scatter plot window backed by matplotlib.

    Parameters
    ----------
    name : str
        Window title.
    observer : Observer
        STARS viewObserver singleton.
    x : array-like, shape (n_cs,)
        Standardised variable values (z-scores).
    y_lag : array-like, shape (n_cs,)
        Spatial lag of x.
    varName : str
        Variable name for axis labels.
    t : int
        Time period index.
    csIds : list
        Cross-sectional ids (default: 0..n-1).
    quad_ids : array-like or None, shape (n_cs,)
        Local Moran quadrant ids (1=HH, 2=LH, 3=LL, 4=HL).
        If None all points are drawn in grey.
    sig_mask : array-like or None, shape (n_cs,) bool
        True where p-value < threshold (significant).  Non-significant
        points are always drawn grey regardless of quad_ids.
    time_string : str
        Human-readable time label appended to title.
    """

    _nms = 0

    def __init__(self, name, observer,
                 x, y_lag, varName, t,
                 csIds=None, quad_ids=None, sig_mask=None,
                 time_string='', width=None, height=None):

        MoranScatterView._nms += 1
        view_name = f'moran_scatter_{MoranScatterView._nms}'
        title = f'Moran Scatter — {name}  {time_string}' if time_string \
            else f'Moran Scatter — {name}'

        self.varName = varName
        self.t = t
        self._x = np.asarray(x, dtype=float)
        self._y = np.asarray(y_lag, dtype=float)
        n = len(self._x)
        self._csIds = list(csIds) if csIds is not None else list(range(n))

        # Quadrant / significance info
        if quad_ids is not None:
            self._quad = np.asarray(quad_ids, dtype=int)
        else:
            self._quad = np.zeros(n, dtype=int)

        if sig_mask is not None:
            self._sig = np.asarray(sig_mask, dtype=bool)
        else:
            self._sig = np.ones(n, dtype=bool)

        # Effective quadrant (0 = not-significant)
        self._eff_quad = np.where(self._sig, self._quad, 0)

        self._cs_to_xy = {cs: (float(self._x[i]), float(self._y[i]))
                          for i, cs in enumerate(self._csIds)}
        self._selected_scatter = None

        super().__init__(view_name, 'scatter', observer,
                         width=width, height=height, title=title)

    # ── Drawing ───────────────────────────────────────────────────────────

    def draw(self):
        """Render the Moran scatter plot."""
        self.ax.clear()
        self._selected_scatter = None

        # Plot points coloured by effective quadrant
        for q in [0, 1, 2, 3, 4]:
            mask = self._eff_quad == q
            if not mask.any():
                continue
            alpha = 0.5 if q == 0 else 0.85
            self.ax.scatter(self._x[mask], self._y[mask],
                            c=_QUAD_COLORS[q], s=16,
                            edgecolors='none', alpha=alpha,
                            zorder=2)

        # Cross-hairs at (mean_x, mean_y)
        mx, my = self._x.mean(), self._y.mean()
        self.ax.axvline(mx, color='black', linewidth=0.6, linestyle='--', zorder=1)
        self.ax.axhline(my, color='black', linewidth=0.6, linestyle='--', zorder=1)

        # OLS line (Moran's I is the slope when data are z-scores)
        if len(self._x) > 1:
            slope, intercept = np.polyfit(self._x, self._y, 1)
            xfit = np.array([self._x.min(), self._x.max()])
            self.ax.plot(xfit, slope * xfit + intercept,
                         color='black', linewidth=1.0, zorder=3,
                         label=f"I = {slope:.4f}")
            self.ax.legend(fontsize=7, loc='upper left')

        self.ax.set_xlabel(f'{self.varName} (standardised)', fontsize=8)
        self.ax.set_ylabel(f'Spatial lag of {self.varName}', fontsize=8)
        self.ax.set_title(f'Moran Scatter — {self.varName}', fontsize=9)
        self.ax.tick_params(labelsize=7)

        # Legend for quadrants
        from matplotlib.patches import Patch
        handles = [
            Patch(facecolor=_QUAD_COLORS[1], label='HH'),
            Patch(facecolor=_QUAD_COLORS[2], label='LH'),
            Patch(facecolor=_QUAD_COLORS[3], label='LL'),
            Patch(facecolor=_QUAD_COLORS[4], label='HL'),
            Patch(facecolor=_QUAD_COLORS[0], label='n.s.'),
        ]
        self.ax.legend(handles=handles, loc='upper left', fontsize=7,
                       framealpha=0.8, title='Quadrant', title_fontsize=7)

    # ── Hit-testing ───────────────────────────────────────────────────────

    def _hit_test(self, x0, y0, x1, y1):
        xmin, xmax = min(x0, x1), max(x0, x1)
        ymin, ymax = min(y0, y1), max(y0, y1)
        return [cs for cs, (cx, cy) in self._cs_to_xy.items()
                if xmin <= cx <= xmax and ymin <= cy <= ymax]

    # ── Highlighting ──────────────────────────────────────────────────────

    def highlightObservations(self, cs_ids):
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

    # ── Time update ───────────────────────────────────────────────────────

    def updateTime(self, ts_id):
        if isinstance(ts_id, (list, tuple)):
            ts_id = ts_id[0]
        if hasattr(self, '_x_full') and self._x_full.ndim == 2:
            self._x = self._x_full[:, ts_id]
            self._y = self._y_full[:, ts_id]
            if hasattr(self, '_quad_full') and self._quad_full.ndim == 2:
                self._quad = self._quad_full[:, ts_id]
            if hasattr(self, '_sig_full') and self._sig_full.ndim == 2:
                self._sig = self._sig_full[:, ts_id]
            self._eff_quad = np.where(self._sig, self._quad, 0)
            self._cs_to_xy = {cs: (float(self._x[i]), float(self._y[i]))
                              for i, cs in enumerate(self._csIds)}
            self.draw()
            self.canvas.draw_idle()
