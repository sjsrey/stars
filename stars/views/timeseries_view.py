"""Time-series view for STARS (Phase 2c).

Replaces gView.TimeSeries (tkinter canvas points + lines) with a
matplotlib line plot.  Each cross-sectional unit is one line; clicking
a time column publishes 'updateTime' so linked views (Map, Histogram …)
switch to that period.

Public interface (mirrors gView.TimeSeries):
  TimeSeriesView(name, observer, values, varName,
                 csIds, tsLabels,
                 time_string)
"""

import sys
import os
import numpy as np

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from views.base import STARSView

_LINE_COLOR = '#4c72b0'
_MEAN_COLOR = '#d62728'
_HIGHLIGHT_COLOR = 'gold'


class TimeSeriesView(STARSView):
    """Time-series window backed by matplotlib.

    Parameters
    ----------
    name : str
        Window title / variable name.
    observer : Observer
        STARS viewObserver singleton.
    values : array-like, shape (n_cs, n_t)  or (n_t,)
        Cross-section × time matrix (or single series).
    varName : str
        Variable name shown in title / y-axis label.
    csIds : list
        Cross-sectional ids (row labels).
    tsLabels : list of str
        Human-readable time period labels (length n_t).
    time_string : str
        Human-readable time label appended to title.
    """

    _nts = 0

    def __init__(self, name, observer,
                 values, varName,
                 csIds=None, tsLabels=None,
                 time_string='', width=None, height=None):

        TimeSeriesView._nts += 1
        view_name = f'ts_{TimeSeriesView._nts}'
        title = f'{name}  {time_string}' if time_string else name

        self.varName = varName
        arr = np.asarray(values, dtype=float)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)   # (1, n_t)
        self._values = arr             # (n_cs, n_t)
        n_cs, n_t = arr.shape

        self._csIds = list(csIds) if csIds is not None else list(range(n_cs))
        self._tsLabels = list(tsLabels) if tsLabels else [str(i) for i in range(n_t)]
        self._n_t = n_t
        self._n_cs = n_cs
        self._selected_t = None
        self._vline = None

        super().__init__(view_name, 'timeSeries', observer,
                         width=width, height=height, title=title)

    # ── Drawing ───────────────────────────────────────────────────────────

    def draw(self):
        """Render all CS lines plus a bold mean line."""
        self.ax.clear()
        t = np.arange(self._n_t)

        # Individual CS lines (thin, semi-transparent)
        for row in self._values:
            self.ax.plot(t, row, color=_LINE_COLOR, alpha=0.25, linewidth=0.7)

        # Mean line
        mean = self._values.mean(axis=0)
        self.ax.plot(t, mean, color=_MEAN_COLOR, linewidth=1.8, zorder=3,
                     label='mean')

        # X-axis ticks
        step = max(1, self._n_t // 10)
        tick_pos = list(range(0, self._n_t, step))
        self.ax.set_xticks(tick_pos)
        self.ax.set_xticklabels([self._tsLabels[i] for i in tick_pos],
                                fontsize=7, rotation=30, ha='right')
        self.ax.set_ylabel(self.varName, fontsize=8)
        self.ax.set_xlabel('Time', fontsize=8)
        self.ax.set_title(self.varName, fontsize=9)
        self.ax.tick_params(axis='y', labelsize=7)
        self.ax.set_xlim(-0.5, self._n_t - 0.5)

        # Restore vertical marker if a time is already selected
        self._vline = None
        if self._selected_t is not None:
            self._draw_vline(self._selected_t)

    def _draw_vline(self, t_idx):
        """Draw / update the vertical selection marker."""
        if self._vline is not None:
            try:
                self._vline.remove()
            except ValueError:
                pass
        self._vline = self.ax.axvline(t_idx, color=_HIGHLIGHT_COLOR,
                                      linewidth=2, zorder=4)

    # ── Hit-testing ───────────────────────────────────────────────────────

    def _hit_test(self, x0, y0, x1, y1):
        """Return the time index nearest to the centre of the selection box.

        The TimeSeries view publishes a single integer time index, not cs_ids.
        We return it wrapped in a list so the base class can call
        selectedObservations([t_idx]).
        """
        x_centre = (x0 + x1) / 2.0
        t_idx = int(round(x_centre))
        t_idx = max(0, min(self._n_t - 1, t_idx))
        return [t_idx]

    # ── Interaction ───────────────────────────────────────────────────────

    def buildMethods(self):
        super().buildMethods()
        self.methods['updateTime'] = self.updateTime

    def selectedObservations(self, obs_ids):
        """Intercept: publish 'updateTime' instead of 'selectedObservations'."""
        if obs_ids:
            t_idx = obs_ids[0]
            self.updateTime(t_idx)
            self.publish('updateTime', t_idx)

    def updateTime(self, ts_id):
        """Respond to a time-period change: move the vertical marker."""
        if isinstance(ts_id, (list, tuple)):
            ts_id = ts_id[0]
        self._selected_t = ts_id
        self._draw_vline(ts_id)
        self.canvas.draw_idle()

    def highlightObservations(self, obs_ids):
        """Treat obs_ids as time indices and move the marker."""
        if obs_ids:
            self.updateTime(obs_ids[0])

    def unhighlightObservations(self, obs_ids):
        if self._vline is not None:
            try:
                self._vline.remove()
            except ValueError:
                pass
            self._vline = None
            self._selected_t = None
            self.canvas.draw_idle()
