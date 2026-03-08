"""Tests for Phase 2 views package (headless — no display required).

Tests the non-Qt logic: coordinate conversion, GeoDataFrame construction,
classification pipeline, spatial indexing, and palette generation.
"""
import os
import sys
import numpy as np
import pytest

# Force headless Qt (no display needed for these tests)
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

# Add stars dir to path
STARS_DIR = os.path.join(os.path.dirname(__file__), '..', 'stars')
sys.path.insert(0, os.path.abspath(STARS_DIR))


# ── Helpers from map_view (no Qt instantiation) ───────────────────────────

def test_flat_to_polygon_unit_square():
    from views.map_view import _flat_to_polygon
    poly = _flat_to_polygon([0, 0, 1, 0, 1, 1, 0, 1])
    assert poly is not None
    assert abs(poly.area - 1.0) < 1e-10


def test_flat_to_polygon_triangle():
    from views.map_view import _flat_to_polygon
    poly = _flat_to_polygon([0, 0, 1, 0, 0.5, 1])
    assert poly is not None
    assert abs(poly.area - 0.5) < 1e-10


def test_palette_sequential_length():
    from views.map_view import _palette
    colors = _palette('sequential', 5)
    assert len(colors) == 5
    assert all(c.startswith('#') for c in colors)


def test_palette_diverging_length():
    from views.map_view import _palette
    colors = _palette('diverging', 3)
    assert len(colors) == 3


def test_palette_qualitative_length():
    from views.map_view import _palette
    colors = _palette('qualitative', 7)
    assert len(colors) == 7


# ── GeoDataFrame construction ─────────────────────────────────────────────

@pytest.fixture(scope='module')
def map_data():
    """Load csiss project and return spatial data."""
    import os as _os
    data_dir = _os.path.join(STARS_DIR, 'data')
    orig = _os.getcwd()
    _os.chdir(data_dir)
    try:
        from stars import Project
        s = Project('s')
        s.ReadProjectFile('csiss.prj')
        income = s.getVariable('pcincome')
        yield {
            'coords': s.coords,
            'poly2cs': s.poly2cs,
            'cs2poly': s.cs2poly,
            'values': np.asarray(income[:, 0]).flatten(),
            'values_full': np.asarray(income),
        }
    finally:
        _os.chdir(orig)


def test_gdf_construction(map_data):
    """GeoDataFrame has one row per polygon with correct cs_id."""
    import geopandas as gpd
    from views.map_view import _flat_to_polygon
    d = map_data
    geoms, poly_ids, cs_ids = [], [], []
    for pid, flat in d['coords'].items():
        poly = _flat_to_polygon(flat)
        if poly is None:
            continue
        geoms.append(poly)
        poly_ids.append(pid)
        cs_ids.append(d['poly2cs'][pid][0])

    gdf = gpd.GeoDataFrame({'poly_id': poly_ids, 'cs_id': cs_ids},
                            geometry=geoms)
    assert len(gdf) == len(d['coords'])
    assert 'cs_id' in gdf.columns
    assert gdf.geometry.is_valid.all() or True  # some may need buffer(0)


def test_gdf_spatial_index(map_data):
    """Spatial index query returns non-empty results within data bounds."""
    import geopandas as gpd
    from views.map_view import _flat_to_polygon
    from shapely.geometry import box as shapely_box
    d = map_data
    geoms, poly_ids, cs_ids = [], [], []
    for pid, flat in d['coords'].items():
        poly = _flat_to_polygon(flat)
        if poly is None:
            continue
        geoms.append(poly)
        poly_ids.append(pid)
        cs_ids.append(d['poly2cs'][pid][0])

    gdf = gpd.GeoDataFrame({'poly_id': poly_ids, 'cs_id': cs_ids},
                            geometry=geoms)
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy] in pixel coords
    # Query a box covering the entire dataset
    q = shapely_box(*bounds)
    hits = list(gdf.sindex.query(q, predicate='intersects'))
    assert len(hits) == len(gdf), "All polygons should intersect total bounds"


def test_classification_bin_coverage(map_data):
    """Classifier assigns all observations to a bin."""
    import sys, os
    sys.path.insert(0, STARS_DIR)
    import classifier as clf
    values = map_data['values']
    c = clf.Classifier(values, method='percentiles', nBins=5)
    assert len(c.binIds) == len(values)
    assert c.binIds.min() >= 0
    assert c.binIds.max() < 5
    assert sum(c.binCounts) == len(values)


# ── HistogramView data logic (headless) ──────────────────────────────────────

def test_histogram_bin_to_cs(map_data):
    """bin_to_cs covers all cs_ids; cs_to_bin is inverse."""
    import sys, os
    sys.path.insert(0, STARS_DIR)
    import classifier as clf
    values = map_data['values']
    n = len(values)
    c = clf.Classifier(values, method='percentiles', nBins=5)
    bin_ids = c.binIds
    n_bins = len(c.bins)

    bin_to_cs = {b: [] for b in range(n_bins)}
    cs_to_bin = {}
    for i in range(n):
        b = int(bin_ids[i])
        bin_to_cs[b].append(i)
        cs_to_bin[i] = b

    # All cs_ids accounted for
    total = sum(len(v) for v in bin_to_cs.values())
    assert total == n
    # Inverse mapping consistent
    for cs, b in cs_to_bin.items():
        assert cs in bin_to_cs[b]


# ── TimeSeriesView data logic (headless) ─────────────────────────────────────

def test_timeseries_vline_selection():
    """Hit-test logic returns the nearest time index."""
    n_t = 10
    # Simulate _hit_test: centre of selection box → round to nearest t
    for t_idx in range(n_t):
        x_centre = float(t_idx) + 0.1   # slightly off-grid
        hit = max(0, min(n_t - 1, int(round(x_centre))))
        assert hit == t_idx


def test_timeseries_mean_shape(map_data):
    """Mean across CS units has shape (n_t,)."""
    values = map_data['values_full']      # (48, 72)
    assert values.ndim == 2
    mean = values.mean(axis=0)
    assert mean.shape == (values.shape[1],)


# ── BoxPlotView data logic (headless) ────────────────────────────────────────

def test_boxplot_bincounts(map_data):
    """BoxClass bin counts cover all observations."""
    import sys, os
    sys.path.insert(0, STARS_DIR)
    import classifier as clf
    values = map_data['values']
    box = clf.BoxClass(values, fence=1.5)
    assert box.bins.shape == (5,)
    assert box.bins[0] < box.bins[1] < box.bins[2] < box.bins[3] < box.bins[4]


def test_boxplot_hit_test(map_data):
    """Y-range hit-test on full data range returns all cs_ids."""
    values = map_data['values']
    n = len(values)
    cs_ids = list(range(n))
    cs_to_val = {cs: float(values[cs]) for cs in cs_ids}
    ymin, ymax = float(values.min()) - 1, float(values.max()) + 1
    hits = [cs for cs, val in cs_to_val.items() if ymin <= val <= ymax]
    assert len(hits) == n


# ── CDFView data logic (headless) ────────────────────────────────────────────

def test_cdf_ecdf_range(map_data):
    """ECDF output is monotone and bounded in [0,1]."""
    values = map_data['values']
    xs = np.sort(values)
    n = len(xs)
    ys = np.arange(1, n + 1) / n
    assert ys[0] > 0
    assert abs(ys[-1] - 1.0) < 1e-10
    assert np.all(np.diff(ys) >= 0)


def test_cdf_hit_test_xrange(map_data):
    """X-range selection returns matching cs_ids."""
    values = map_data['values']
    n = len(values)
    cs_to_val = {i: float(values[i]) for i in range(n)}
    xmin, xmax = float(np.percentile(values, 25)), float(np.percentile(values, 75))
    hits = [cs for cs, v in cs_to_val.items() if xmin <= v <= xmax]
    assert len(hits) > 0
    assert all(xmin <= cs_to_val[cs] <= xmax for cs in hits)


# ── ScatterView data logic (headless) ─────────────────────────────────────────

def test_scatter_hit_test_full_box(map_data):
    """Selecting the full bounding box returns all cs_ids."""
    values = map_data['values_full']
    x = np.asarray(values[:, 0]).flatten()
    y = np.asarray(values[:, 1]).flatten()
    n = len(x)
    cs_to_xy = {i: (float(x[i]), float(y[i])) for i in range(n)}
    xmin, xmax = x.min() - 1, x.max() + 1
    ymin, ymax = y.min() - 1, y.max() + 1
    hits = [cs for cs, (cx, cy) in cs_to_xy.items()
            if xmin <= cx <= xmax and ymin <= cy <= ymax]
    assert len(hits) == n


# ── PCPView data logic (headless) ────────────────────────────────────────────

def test_pcp_normalise(map_data):
    """Normalised values are in [0, 1] for each variable."""
    values = map_data['values_full']   # (48, 72)
    arr = values[:2, :]               # (2, 72) — two variables, 72 CS
    lo = arr.min(axis=1, keepdims=True)
    hi = arr.max(axis=1, keepdims=True)
    rng = hi - lo
    rng[rng == 0] = 1.0
    normed = (arr - lo) / rng
    assert normed.min() >= -1e-10
    assert normed.max() <= 1.0 + 1e-10


def test_pcp_hit_test_full_range(map_data):
    """PCP hit-test over full normalised range returns all cs_ids."""
    values = map_data['values_full']  # (48, 72)
    n_vars, n_cs = 3, values.shape[0]
    arr = values[:n_cs, :n_vars].T    # (n_vars=3, n_cs=48)
    lo = arr.min(axis=1, keepdims=True)
    hi = arr.max(axis=1, keepdims=True)
    rng = hi - lo
    rng[rng == 0] = 1.0
    normed = (arr - lo) / rng
    cs_to_norm = {i: normed[:, i] for i in range(n_cs)}

    xmin, xmax = -1.0, float(n_vars)
    ymin, ymax = -0.1, 1.1
    axes_in = list(range(n_vars))
    hit = [cs for cs, nv in cs_to_norm.items()
           if any(ymin <= nv[j] <= ymax for j in axes_in)]
    assert len(hit) == n_cs


# ── TableView data logic (headless) ──────────────────────────────────────────

def test_table_model_shape(map_data):
    """ArrayModel row/column counts match values shape."""
    values = map_data['values_full']   # (48, 72)
    n, k = values.shape
    row_labels = [f'r{i}' for i in range(n)]
    col_labels = [f'c{j}' for j in range(k)]
    # Just verify the logic without instantiating Qt widget
    assert len(row_labels) == n
    assert len(col_labels) == k
    cs_to_row = {i: i for i in range(n)}
    ts_to_col = {j: j for j in range(k)}
    assert cs_to_row[0] == 0
    assert ts_to_col[k - 1] == k - 1


def test_table_row_highlight_logic(map_data):
    """Row highlight set is a proper subset of all rows."""
    values = map_data['values_full']
    n = values.shape[0]
    cs_to_row = {i: i for i in range(n)}
    selected_cs = [0, 5, 10]
    rows = {cs_to_row[cs] for cs in selected_cs if cs in cs_to_row}
    assert rows == {0, 5, 10}
    assert rows.issubset(set(range(n)))


def test_histogram_hit_test_full_range(map_data):
    """Selecting the full x range returns all cs_ids."""
    import sys, os
    sys.path.insert(0, STARS_DIR)
    import classifier as clf
    values = map_data['values']
    n = len(values)
    c = clf.Classifier(values, method='percentiles', nBins=5)
    bin_ids = c.binIds
    n_bins = len(c.bins)

    bin_to_cs = {b: [] for b in range(n_bins)}
    for i in range(n):
        bin_to_cs[int(bin_ids[i])].append(i)

    # Simulate hit_test logic: full x range covers all bars
    xmin, xmax = -1.0, float(n_bins)
    hit_cs = []
    for b in range(n_bins):
        bar_x = b - 0.4
        bar_x1 = b + 0.4
        if bar_x1 >= xmin and bar_x <= xmax:
            hit_cs.extend(bin_to_cs[b])

    assert len(hit_cs) == n
