"""Numerical equivalence tests for Esda Geary and LocalMoran (Phase 1b)."""
import numpy as np
import pytest


def test_geary_length(csiss):
    from Esda import Geary
    gc = Geary(csiss['income'], csiss['wsp'])
    assert len(gc.gc) == 72


def test_geary_gc70(csiss):
    from Esda import Geary
    gc = Geary(csiss['income'], csiss['wsp'])
    np.testing.assert_allclose(gc.gc[70], 0.6477454386791032, rtol=1e-6)


def test_geary_gc0(csiss):
    from Esda import Geary
    gc = Geary(csiss['income'], csiss['wsp'])
    np.testing.assert_allclose(gc.gc[0], 0.36841662488184035, rtol=1e-6)


def test_geary_attrs(csiss):
    from Esda import Geary
    gc = Geary(csiss['income'], csiss['wsp'])
    assert gc.gc.shape == (72,)
    assert gc.zc.shape == (72,)
    assert len(gc.zpvalue) == 72
    assert hasattr(gc, 'vc')
    assert hasattr(gc, 'sc')


def test_geary_less_than_one(csiss):
    """Income has strong positive spatial autocorrelation -> Geary C < 1."""
    from Esda import Geary
    gc = Geary(csiss['income'], csiss['wsp'])
    assert np.all(gc.gc < 1.0), "Expected C < 1 (positive autocorrelation)"


def test_localmoran_shape(csiss):
    from Esda import LocalMoran
    lm = LocalMoran(csiss['income'], csiss['wsp'])
    assert lm.mi.shape == (48, 72)
    assert lm.qvalue.shape == (48, 72)
    assert lm.dvalue.shape == (48, 72)
    assert lm.expMi.shape == (48, 1)
    assert lm.ylag.shape == (48, 72)


def test_localmoran_expmoi(csiss):
    from Esda import LocalMoran
    lm = LocalMoran(csiss['income'], csiss['wsp'])
    expected = -1.0 / 47
    np.testing.assert_allclose(lm.expMi, expected, rtol=1e-10)


def test_localmoran_quadrants_valid(csiss):
    from Esda import LocalMoran
    lm = LocalMoran(csiss['income'], csiss['wsp'])
    assert set(np.unique(lm.qvalue)).issubset({1, 2, 3, 4})
    assert set(np.unique(lm.dvalue)).issubset({1, 2, 3, 4})
