"""Empirical CDF view for STARS (Phase 2c).

Replaces gView.CDF (tkinter canvas line segments via KDE) with a
matplotlib step plot of the empirical CDF.

Public interface (mirrors gView.CDF):
  CDFView(name, observer, values, varName, t,
          csIds, tsIds, time_string)
"""

import sys
import os
import numpy as np

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from views.base import STARSView

_LINE_COLOR = '#4c72b0'
_HIGHLIGHT_COLOR = 'gold'


class CDFView(STARSView):
    """Empirical CDF window backed by matplotlib.

    Parameters
    ----------
    name : str
        Window title / variable name.
    observer : Observer
        STARS viewObserver singleton.
    values : array-like, shape (n_cs,)
        One value per cross-sectional unit (current time period).
    varName : str
        Variable name shown in title / x-axis label.
    t : int
        Time period index.
    csIds : list
        Cross-sectional ids corresponding to values (default: 0..n-1).
    tsIds : list
        Time-series ids (passed through; not used in rendering).
    time_string : str
        Human-readable time label appended to title.
    """

    _ncdf = 0

    def __init__(self, name, observer,
                 values, varName, t,
                 csIds=None, tsIds=None,
                 time_string='', width=None, height=None):

        CDFView._ncdf += 1
        view_name = f'cdf_{CDFView._ncdf}'
        title = f'{name}  {time_string}' if time_string else name

        self.varName = varName
        self.t = t
        self._values_1d = np.asarray(values, dtype=float)
        self._csIds = list(csIds) if csIds is not None else list(range(len(self._values_1d)))
        self._tsIds = tsIds or []
        self._cs_to_val = {cs: self._values_1d[i]
                           for i, cs in enumerate(self._csIds)}
        self._selected_scatter = None

        super().__init__(view_name, 'CDF', observer,
                         width=width, height=height, title=title)

    # ── Drawing ───────────────────────────────────────────────────────────

    def _ecdf(self, x):
        """Return (sorted_x, F(x)) for the empirical CDF."""
        xs = np.sort(x)
        n = len(xs)
        ys = np.arange(1, n + 1) / n
        return xs, ys

    def draw(self):
        """Render the step-function empirical CDF."""
        self.ax.clear()
        self._selected_scatter = None
        xs, ys = self._ecdf(self._values_1d)
        self.ax.step(xs, ys, where='post', color=_LINE_COLOR, linewidth=1.2)
        self.ax.set_xlabel(self.varName, fontsize=8)
        self.ax.set_ylabel('F(x)', fontsize=8)
        self.ax.set_title(f'Empirical CDF — {self.varName}', fontsize=9)
        self.ax.tick_params(labelsize=7)
        self.ax.set_ylim(-0.02, 1.05)

    # ── Hit-testing ───────────────────────────────────────────────────────

    def _hit_test(self, x0, y0, x1, y1):
        """Return cs_ids whose x values fall within the selection x range."""
        xmin, xmax = min(x0, x1), max(x0, x1)
        return [cs for cs, val in self._cs_to_val.items()
                if xmin <= val <= xmax]

    # ── Highlighting ──────────────────────────────────────────────────────

    def highlightObservations(self, cs_ids):
        """Mark selected observations as vertical tick marks on the CDF."""
        if self._selected_scatter is not None:
            try:
                self._selected_scatter.remove()
            except ValueError:
                pass
            self._selected_scatter = None

        if not cs_ids:
            return

        cs_set = set(cs_ids)
        xvals = [self._cs_to_val[cs] for cs in cs_set if cs in self._cs_to_val]
        if not xvals:
            return

        # Compute CDF values at each selected point
        xs_sorted, ys_ecdf = self._ecdf(self._values_1d)
        yvals = [float(ys_ecdf[np.searchsorted(xs_sorted, v, side='right') - 1])
                 for v in xvals]

        self._selected_scatter = self.ax.scatter(
            xvals, yvals, color=_HIGHLIGHT_COLOR,
            edgecolors='black', linewidths=0.5,
            s=30, zorder=5)

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
        if hasattr(self, '_values_full') and self._values_full.ndim == 2:
            self._values_1d = self._values_full[:, ts_id]
            self._cs_to_val = {cs: self._values_1d[i]
                               for i, cs in enumerate(self._csIds)}
            self.draw()
            self.canvas.draw_idle()
