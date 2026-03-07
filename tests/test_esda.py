"""Numerical equivalence tests for Esda module (Phase 1b)."""
import numpy as np
import pytest


def test_moran_shape(csiss):
    from Esda import Moran
    m = Moran(csiss['income'], csiss['wsp'])
    assert m.mi.shape == (72,)
    assert m.zi.shape == (72,)
    assert len(m.npvalue) == 72


def test_moran_mi70(csiss):
    from Esda import Moran
    m = Moran(csiss['income'], csiss['wsp'])
    # Reference value from stars.py docstring
    np.testing.assert_allclose(m.mi[70], 0.350700349569403, rtol=1e-6)


def test_moran_ei(csiss):
    from Esda import Moran
    m = Moran(csiss['income'], csiss['wsp'])
    # ei = -1/(n-1) = -1/47
    np.testing.assert_allclose(m.ei, -1.0 / 47, rtol=1e-10)


def test_moran_ylag_shape(csiss):
    from Esda import Moran
    m = Moran(csiss['income'], csiss['wsp'])
    assert m.ylag.shape == (48, 72)


def test_moran_positive_autocorrelation(csiss):
    """Income has strong positive spatial autocorrelation in all periods."""
    from Esda import Moran
    m = Moran(csiss['income'], csiss['wsp'])
    assert np.all(m.mi > 0), "Expected positive Moran's I for income"
