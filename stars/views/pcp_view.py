"""Parallel Coordinates Plot view for STARS (Phase 2c).

Replaces gView.PCP (tkinter canvas connector lines) with matplotlib.
Each cross-sectional unit is a polyline connecting its normalised value
on each variable axis.  An optional z variable colours the lines.

Public interface (mirrors gView.PCP):
  PCPView(name, observer, varNames, values, t,
          csIds, z, zLabel, nColors, time_string)
"""

import sys
import os
import numpy as np

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from views.base import STARSView

_DEFAULT_COLOR = 'steelblue'
_HIGHLIGHT_COLOR = 'gold'
_DEFAULT_ALPHA = 0.35


class PCPView(STARSView):
    """Parallel coordinates window backed by matplotlib.

    Parameters
    ----------
    name : str
        Window title.
    observer : Observer
        STARS viewObserver singleton.
    varNames : list of str
        Variable names — one axis per entry.
    values : array-like, shape (n_vars, n_cs)
        One row per variable, one column per CS unit.
        Alternatively (n_cs, n_vars) if ``transpose=True``.
    t : int
        Time period index (for display only).
    csIds : list
        Cross-sectional ids (default: 0..n_cs-1).
    z : array-like or None, shape (n_cs,)
        Optional colouring variable.
    zLabel : str
        Label for z variable.
    nColors : int
        Number of colour classes for z (default 6).
    time_string : str
        Human-readable time label appended to title.
    transpose : bool
        If True, ``values`` is (n_cs, n_vars); transpose before use.
    """

    _npcp = 0

    def __init__(self, name, observer,
                 varNames, values, t,
                 csIds=None, z=None, zLabel='Z', nColors=6,
                 time_string='', transpose=False,
                 width=None, height=None):

        PCPView._npcp += 1
        view_name = f'pcp_{PCPView._npcp}'
        title = f'{name}  {time_string}' if time_string else name

        self.varNames = list(varNames)
        arr = np.asarray(values, dtype=float)
        if transpose:
            arr = arr.T          # now (n_vars, n_cs)
        # arr shape: (n_vars, n_cs)
        self._data = arr         # each row is one variable
        n_vars, n_cs = arr.shape

        self._csIds = list(csIds) if csIds is not None else list(range(n_cs))
        self._z = np.asarray(z, dtype=float) if z is not None else None
        self.zLabel = zLabel
        self.nColors = nColors
        self.t = t

        # Normalise each variable to [0, 1]
        self._norm = self._normalise(arr)   # (n_vars, n_cs)

        # Precompute per-cs line colors from z
        self._line_colors = self._make_colors()

        # cs_id → normalised values for hit-testing
        self._cs_to_norm = {cs: self._norm[:, i]
                            for i, cs in enumerate(self._csIds)}

        self._highlight_lines = []

        super().__init__(view_name, 'PCP', observer,
                         width=width, height=height, title=title)

    # ── Internal helpers ──────────────────────────────────────────────────

    @staticmethod
    def _normalise(arr):
        """Normalise each row (variable) to [0, 1], handling zero-range."""
        lo = arr.min(axis=1, keepdims=True)
        hi = arr.max(axis=1, keepdims=True)
        rng = hi - lo
        rng[rng == 0] = 1.0
        return (arr - lo) / rng

    def _make_colors(self):
        """Return per-cs colour strings based on z (or default)."""
        if self._z is None:
            return [_DEFAULT_COLOR] * self._norm.shape[1]
        # Quantise z into nColors bins using linspace
        z = self._z
        lo, hi = z.min(), z.max()
        if hi == lo:
            return [_DEFAULT_COLOR] * len(z)
        import matplotlib.cm as cm
        cmap = cm.get_cmap('RdYlBu_r', self.nColors)
        normed = (z - lo) / (hi - lo)
        return [cmap(v) for v in normed]

    # ── Drawing ───────────────────────────────────────────────────────────

    def draw(self):
        """Render the parallel coordinates plot."""
        self.ax.clear()
        self._highlight_lines = []

        n_vars, n_cs = self._norm.shape
        x_positions = np.arange(n_vars)

        # Draw one polyline per CS unit
        self._cs_line_map = {}    # cs_id → list of Line2D objects
        for i, cs in enumerate(self._csIds):
            yvals = self._norm[:, i]
            color = self._line_colors[i]
            lines = self.ax.plot(x_positions, yvals, color=color,
                                 alpha=_DEFAULT_ALPHA, linewidth=0.7)
            self._cs_line_map[cs] = lines

        # Draw vertical axis bars
        for xp in x_positions:
            self.ax.axvline(xp, color='black', linewidth=0.8, zorder=3)

        # Axis labels
        self.ax.set_xticks(x_positions)
        self.ax.set_xticklabels(self.varNames, fontsize=7, rotation=20, ha='right')
        self.ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
        self.ax.set_yticklabels(['min', '25%', '50%', '75%', 'max'], fontsize=7)
        self.ax.set_xlim(-0.3, n_vars - 0.7)
        self.ax.set_ylim(-0.05, 1.05)
        self.ax.set_title('Parallel Coordinates — ' + '  '.join(self.varNames[:3]) +
                          ('…' if len(self.varNames) > 3 else ''), fontsize=9)

        # Colorbar for z
        if self._z is not None:
            import matplotlib.cm as cm
            import matplotlib.colors as mcolors
            lo, hi = self._z.min(), self._z.max()
            sm = cm.ScalarMappable(cmap='RdYlBu_r',
                                   norm=mcolors.Normalize(lo, hi))
            sm.set_array([])
            self.fig.colorbar(sm, ax=self.ax, label=self.zLabel, shrink=0.8)

    # ── Subscriber overrides ──────────────────────────────────────────────

    def buildMethods(self):
        super().buildMethods()
        self.methods.update({
            'newSelectObservations': self.selectObservations,
        })

    def selectedObservations(self, obs_ids):
        """PCP publishes 'newSelectedObservations' for Interaction.py routing."""
        self.selectObservations(obs_ids)
        self.publish('newSelectedObservations', obs_ids)

    # ── Hit-testing ───────────────────────────────────────────────────────

    def _hit_test(self, x0, y0, x1, y1):
        """Return cs_ids whose polylines pass through the selection box.

        Strategy: find which axis columns fall in the x range, then check
        whether any of those normalised y values fall in the y range.
        """
        xmin, xmax = min(x0, x1), max(x0, x1)
        ymin, ymax = min(y0, y1), max(y0, y1)
        n_vars = len(self.varNames)
        # Which axis indices are within the x selection?
        axes_in_range = [j for j in range(n_vars)
                         if xmin <= j <= xmax]
        if not axes_in_range:
            return []
        hit = []
        for cs, norm_vals in self._cs_to_norm.items():
            for j in axes_in_range:
                if ymin <= norm_vals[j] <= ymax:
                    hit.append(cs)
                    break
        return hit

    # ── Highlighting ──────────────────────────────────────────────────────

    def highlightObservations(self, cs_ids):
        """Recolour selected CS lines yellow and bring to front."""
        # Restore previously highlighted lines
        for cs, lines in self._highlight_lines:
            orig_color = self._line_colors[self._csIds.index(cs)] \
                if cs in self._csIds else _DEFAULT_COLOR
            for ln in lines:
                ln.set_color(orig_color)
                ln.set_alpha(_DEFAULT_ALPHA)
                ln.set_linewidth(0.7)
                ln.set_zorder(2)

        self._highlight_lines = []
        cs_set = set(cs_ids)
        for cs in cs_set:
            lines = self._cs_line_map.get(cs)
            if lines:
                for ln in lines:
                    ln.set_color(_HIGHLIGHT_COLOR)
                    ln.set_alpha(1.0)
                    ln.set_linewidth(1.5)
                    ln.set_zorder(5)
                self._highlight_lines.append((cs, lines))

    def unhighlightObservations(self, cs_ids):
        cs_set = set(cs_ids)
        remaining = []
        for cs, lines in self._highlight_lines:
            if cs in cs_set:
                idx = self._csIds.index(cs) if cs in self._csIds else None
                orig_color = self._line_colors[idx] if idx is not None else _DEFAULT_COLOR
                for ln in lines:
                    ln.set_color(orig_color)
                    ln.set_alpha(_DEFAULT_ALPHA)
                    ln.set_linewidth(0.7)
                    ln.set_zorder(2)
            else:
                remaining.append((cs, lines))
        self._highlight_lines = remaining
        self.canvas.draw_idle()

    # ── Time update ───────────────────────────────────────────────────────

    def updateTime(self, ts_id):
        """Switch to a new time period (requires _data_full of shape
        (n_vars, n_cs, n_t))."""
        if isinstance(ts_id, (list, tuple)):
            ts_id = ts_id[0]
        if hasattr(self, '_data_full') and self._data_full.ndim == 3:
            self._data = self._data_full[:, :, ts_id]
            self._norm = self._normalise(self._data)
            self._cs_to_norm = {cs: self._norm[:, i]
                                for i, cs in enumerate(self._csIds)}
            self.draw()
            self.canvas.draw_idle()
