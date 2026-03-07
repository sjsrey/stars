"""Tests for pysal_weights adapter (Phase 1a)."""
import numpy as np
import pytest


def test_spmatrix_to_w_sparse(csiss):
    from pysal_weights import spmatrix_to_w
    w = spmatrix_to_w(csiss['wsp'])
    assert w.n == 48
    assert w.transform.lower() == 'r'
    # Row sums should be ~1 for row-standardized (non-islands)
    full, _ = w.full()
    row_sums = full.sum(axis=1)
    assert np.allclose(row_sums[row_sums > 0], 1.0, rtol=1e-6)


def test_stars_weights_from_shapefile(tmp_path, csiss):
    """STARSWeights.from_shapefile produces list-indexed neighbors."""
    import os
    data_dir = os.path.join(
        os.path.dirname(__file__), '..', 'stars', 'data'
    )
    shp = os.path.join(data_dir, 'california.shp')
    if not os.path.exists(shp):
        pytest.skip('california.shp not available')
    from pysal_weights import STARSWeights
    sw = STARSWeights.from_shapefile(shp, wt_type='rook')
    assert isinstance(sw.neighbors, list)
    assert isinstance(sw.numneigh, list)
    assert all(sw.numneigh[i] == len(sw.neighbors[i])
               for i in range(len(sw.numneigh)))


def test_spmatrix_to_w_roundtrip(csiss):
    """Full matrix via spmatrix_to_w matches spMatrix.full()."""
    from pysal_weights import spmatrix_to_w
    wsp = csiss['wsp']
    stars_full = wsp.full()
    w = spmatrix_to_w(wsp)
    pysal_full, _ = w.full()
    np.testing.assert_allclose(stars_full, pysal_full, rtol=1e-6)
