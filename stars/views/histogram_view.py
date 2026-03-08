"""Histogram view for STARS (Phase 2c).

Replaces gView.Histogram (tkinter canvas.create_rectangle per observation)
with a matplotlib bar chart backed by the same Classifier pipeline.

Public interface (mirrors gView.Histogram):
  HistogramView(name, observer, values, varName, t,
                csIds, tsIds,
                classification, nBins, bins,
                time_string)

Linking/brushing semantics mirror the original:
  - A selection rectangle in x selects entire bins (not individual obs).
  - Highlighted bars are recoloured yellow; deselection restores the default.
"""

import sys
import os
import numpy as np

_STARS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _STARS_DIR not in sys.path:
    sys.path.insert(0, _STARS_DIR)

from views.base import STARSView
import classifier as _clf

_DEFAULT_COLOR = '#4c72b0'
_HIGHLIGHT_COLOR = '#ffff00'


class HistogramView(STARSView):
    """Histogram window backed by matplotlib bar chart.

    Parameters
    ----------
    name : str
        Window title / variable name.
    observer : Observer
        STARS viewObserver singleton.
    values : array-like, shape (n_cs,)
        Scalar values for the current time period.
    varName : str
        Variable name shown in title.
    t : int
        Time period index.
    csIds : list
        Cross-sectional ids corresponding to values (default: 0..n-1).
    tsIds : list
        Time-series ids (passed through; not used in rendering).
    classification : str
        Classifier method ('percentiles', 'equalWidth', 'sturges', ...).
    nBins : int
        Number of bins.
    bins : list
        Pre-specified bin edges (empty = compute from data).
    time_string : str
        Human-readable time label appended to title.
    """

    _nhist = 0

    def __init__(self, name, observer,
                 values, varName, t,
                 csIds=None, tsIds=None,
                 classification='sturges', nBins=5, bins=None,
                 time_string='', width=None, height=None):

        HistogramView._nhist += 1
        view_name = f'hist_{HistogramView._nhist}'
        title = f'{name}  {time_string}' if time_string else name

        self.varName = varName
        self.t = t
        self._values_1d = np.asarray(values, dtype=float)
        self._csIds = list(csIds) if csIds is not None else list(range(len(self._values_1d)))
        self._tsIds = tsIds or []
        self.classification = classification
        self.nBins = nBins
        self._bins_input = bins or []

        # Build bin structure from classifier
        self._classify()

        super().__init__(view_name, 'histogram', observer,
                         width=width, height=height, title=title)

    # ── Classification ────────────────────────────────────────────────────

    def _classify(self):
        """Run classifier and build bin→cs and cs→bin mappings."""
        clf = _clf.Classifier(self._values_1d,
                              method=self.classification,
                              nBins=self.nBins,
                              bins=self._bins_input)
        bin_ids = clf.binIds          # (n_cs,) int array
        self._bounds = clf.bins       # list of bin-edge values (n_bins,)
        n_bins = len(self._bounds)

        # bin_to_cs: {bin_idx: [cs_id, ...]}
        self._bin_to_cs = {b: [] for b in range(n_bins)}
        self._cs_to_bin = {}
        for i, cs in enumerate(self._csIds):
            b = int(bin_ids[i])
            self._bin_to_cs[b].append(cs)
            self._cs_to_bin[cs] = b

        self._n_bins = n_bins
        self._counts = np.array([len(self._bin_to_cs[b]) for b in range(n_bins)],
                                dtype=float)

    # ── Drawing ───────────────────────────────────────────────────────────

    def draw(self):
        """Render the histogram as a bar chart."""
        self.ax.clear()
        x = np.arange(self._n_bins)
        self._bars = self.ax.bar(x, self._counts, color=_DEFAULT_COLOR,
                                 edgecolor='black', linewidth=0.5, width=0.8)
        self._selected_bins = set()

        # X-axis tick labels: bin boundaries
        labels = [f'{v:.2f}' for v in self._bounds]
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(labels, fontsize=7, rotation=30, ha='right')

        self.ax.set_ylabel('Observations', fontsize=8)
        self.ax.set_xlabel(self.varName, fontsize=8)
        self.ax.set_title(self.varName, fontsize=9)
        self.ax.tick_params(axis='y', labelsize=7)

    # ── Selection / brushing ──────────────────────────────────────────────

    def buildMethods(self):
        super().buildMethods()
        # No extra method keys needed — standard selectObservations is used

    def _hit_test(self, x0, y0, x1, y1):
        """Return cs_ids whose bins overlap the x range [min(x0,x1), max(x0,x1)]."""
        xmin, xmax = min(x0, x1), max(x0, x1)
        cs_ids = []
        for b in range(self._n_bins):
            bar_x = b - 0.4   # left edge of bar (width=0.8, centred at b)
            bar_x1 = b + 0.4  # right edge
            if bar_x1 >= xmin and bar_x <= xmax:
                cs_ids.extend(self._bin_to_cs[b])
        return cs_ids

    def highlightObservations(self, cs_ids):
        """Recolour bars that contain any of the given cs_ids."""
        if not hasattr(self, '_bars') or self._bars is None:
            return
        cs_set = set(cs_ids)
        # Find which bins contain at least one selected cs_id
        highlighted = set()
        for cs in cs_set:
            b = self._cs_to_bin.get(cs)
            if b is not None:
                highlighted.add(b)
        self._selected_bins = highlighted
        for b, bar in enumerate(self._bars):
            bar.set_facecolor(_HIGHLIGHT_COLOR if b in highlighted else _DEFAULT_COLOR)

    def unhighlightObservations(self, cs_ids):
        """Restore default colour for bars containing cs_ids."""
        if not hasattr(self, '_bars') or self._bars is None:
            return
        cs_set = set(cs_ids)
        for cs in cs_set:
            b = self._cs_to_bin.get(cs)
            if b is not None and b in self._selected_bins:
                self._selected_bins.discard(b)
                self._bars[b].set_facecolor(_DEFAULT_COLOR)

    # ── Time update ───────────────────────────────────────────────────────

    def updateTime(self, ts_id):
        """Switch to a new time period (requires full values_full array)."""
        if isinstance(ts_id, (list, tuple)):
            ts_id = ts_id[0]
        if hasattr(self, '_values_full') and self._values_full.ndim == 2:
            self._values_1d = self._values_full[:, ts_id]
            self._classify()
            self.draw()
            self.canvas.draw_idle()
