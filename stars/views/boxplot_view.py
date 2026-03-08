"""Box-plot view for STARS (Phase 2c).

Replaces gView.BoxPlot (tkinter canvas rectangles + ovals) with a
matplotlib boxplot.  Highlighting overlays selected points as coloured
scatter markers.

Public interface (mirrors gView.BoxPlot):
  BoxPlotView(name, observer, values, varName, t,
              csIds, tsIds, fence, time_string)
"""

import sys
import os
import numpy as np

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from views.base import STARSView
import classifier as _clf

_OUTLIER_COLOR = '#d62728'
_HIGHLIGHT_COLOR = 'gold'


class BoxPlotView(STARSView):
    """Box-plot window backed by matplotlib.

    Parameters
    ----------
    name : str
        Window title / variable name.
    observer : Observer
        STARS viewObserver singleton.
    values : array-like, shape (n_cs,)
        One value per cross-sectional unit (current time period).
    varName : str
        Variable name shown in title / y-axis label.
    t : int
        Time period index.
    csIds : list
        Cross-sectional ids corresponding to values (default: 0..n-1).
    tsIds : list
        Time-series ids (passed through; not used in rendering).
    fence : float
        IQR multiplier for fence length (default 1.5).
    time_string : str
        Human-readable time label appended to title.
    """

    _nbox = 0

    def __init__(self, name, observer,
                 values, varName, t,
                 csIds=None, tsIds=None, fence=1.5,
                 time_string='', width=None, height=None):

        BoxPlotView._nbox += 1
        view_name = f'boxplot_{BoxPlotView._nbox}'
        title = f'{name}  {time_string}' if time_string else name

        self.varName = varName
        self.t = t
        self._values_1d = np.asarray(values, dtype=float)
        self._csIds = list(csIds) if csIds is not None else list(range(len(self._values_1d)))
        self._tsIds = tsIds or []
        self.fence = fence
        self._selected_scatter = None

        # Compute box statistics for hit-testing
        self._box = _clf.BoxClass(self._values_1d, fence=fence)
        # cs_id → value (for y-range hit-testing)
        self._cs_to_val = {cs: self._values_1d[i]
                           for i, cs in enumerate(self._csIds)}

        super().__init__(view_name, 'boxplot', observer,
                         width=width, height=height, title=title)

    # ── Drawing ───────────────────────────────────────────────────────────

    def draw(self):
        """Render the box plot."""
        self.ax.clear()
        self._selected_scatter = None

        bp = self.ax.boxplot(self._values_1d, whis=self.fence,
                             patch_artist=True,
                             medianprops=dict(color='black', linewidth=1.5),
                             boxprops=dict(facecolor='#aec7e8', linewidth=1),
                             flierprops=dict(marker='o', markerfacecolor=_OUTLIER_COLOR,
                                            markersize=4, linestyle='none',
                                            markeredgewidth=0))
        self.ax.set_ylabel(self.varName, fontsize=8)
        self.ax.set_xticks([1])
        self.ax.set_xticklabels([self.varName], fontsize=8)
        self.ax.tick_params(axis='y', labelsize=7)
        self.ax.set_title(self.varName, fontsize=9)
        self._bp = bp

    # ── Hit-testing ───────────────────────────────────────────────────────

    def _hit_test(self, x0, y0, x1, y1):
        """Return cs_ids whose values fall within the y range of the box."""
        ymin, ymax = min(y0, y1), max(y0, y1)
        return [cs for cs, val in self._cs_to_val.items()
                if ymin <= val <= ymax]

    # ── Highlighting ──────────────────────────────────────────────────────

    def highlightObservations(self, cs_ids):
        """Overlay selected points as yellow scatter markers."""
        # Remove previous highlight
        if self._selected_scatter is not None:
            try:
                self._selected_scatter.remove()
            except ValueError:
                pass
            self._selected_scatter = None

        if not cs_ids:
            return

        cs_set = set(cs_ids)
        yvals = [self._cs_to_val[cs] for cs in cs_set if cs in self._cs_to_val]
        if not yvals:
            return
        x_jitter = np.ones(len(yvals))  # all at x=1 (the single box column)
        self._selected_scatter = self.ax.scatter(
            x_jitter, yvals, color=_HIGHLIGHT_COLOR,
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
        """Switch to a new time period."""
        if isinstance(ts_id, (list, tuple)):
            ts_id = ts_id[0]
        if hasattr(self, '_values_full') and self._values_full.ndim == 2:
            self._values_1d = self._values_full[:, ts_id]
            self._box = _clf.BoxClass(self._values_1d, fence=self.fence)
            self._cs_to_val = {cs: self._values_1d[i]
                               for i, cs in enumerate(self._csIds)}
            self.draw()
            self.canvas.draw_idle()
