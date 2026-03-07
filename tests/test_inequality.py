"""Numerical equivalence tests for Inequality module (Phase 1d)."""
import numpy as np
import pytest


def test_theil_length(csiss):
    from Inequality import Theil
    t = Theil(csiss['income'])
    assert len(t.T) == 72


def test_theil_t0(csiss):
    from Inequality import Theil
    t = Theil(csiss['income'])
    np.testing.assert_allclose(t.T[0], 0.062513504720263305, rtol=1e-6)


def test_theil_t_last(csiss):
    from Inequality import Theil
    t = Theil(csiss['income'])
    np.testing.assert_allclose(t.T[-1], 0.011588740522236757, rtol=1e-6)


def test_theild_bg0(csiss):
    from Inequality import TheilD
    td = TheilD(csiss['income'], csiss['region'])
    np.testing.assert_allclose(td.BG[0], 0.04896375187589095, rtol=1e-6)


def test_theild_wg0(csiss):
    from Inequality import TheilD
    td = TheilD(csiss['income'], csiss['region'])
    np.testing.assert_allclose(td.WG[0], 0.013549752844372355, rtol=1e-6)


def test_theild_t_equals_bg_plus_wg(csiss):
    from Inequality import TheilD
    td = TheilD(csiss['income'], csiss['region'])
    np.testing.assert_allclose(td.T, td.BG + td.WG, rtol=1e-10)


def test_theild_attrs(csiss):
    from Inequality import TheilD
    td = TheilD(csiss['income'], csiss['region'])
    assert td.sig is None
    assert td.wgg is None
    assert td.p is not None
    assert td.pid is not None
