"""Tests for Markov module (Phase 1c)."""
import numpy as np
import pytest


def test_clmarkov_transmat(csiss):
    from Markov import ClMarkov
    cm = ClMarkov(csiss['income'])
    assert cm.transMat[0, 0] == 208
    assert cm.transMat.sum() == 3408


def test_clmarkov_k(csiss):
    from Markov import ClMarkov
    cm = ClMarkov(csiss['income'])
    assert cm.k == 5


def test_clmarkov_pmat_rowsums(csiss):
    from Markov import ClMarkov
    cm = ClMarkov(csiss['income'])
    np.testing.assert_allclose(cm.pMat.sum(axis=1), 1.0, rtol=1e-10)


def test_clmarkov_pmat_values(csiss):
    from Markov import ClMarkov
    cm = ClMarkov(csiss['income'])
    np.testing.assert_allclose(cm.pMat[0, 0], 0.82868526, rtol=1e-6)


def test_clmarkov_edist_sums_to_one(csiss):
    from Markov import ClMarkov
    cm = ClMarkov(csiss['income'])
    np.testing.assert_allclose(cm.edist.sum(), 1.0, rtol=1e-10)


def test_clmarkov_edist_values(csiss):
    """Ergodic distribution: income is very persistent in top class."""
    from Markov import ClMarkov
    cm = ClMarkov(csiss['income'])
    np.testing.assert_allclose(cm.edist[4], 0.97385295, rtol=1e-5)
    assert cm.edist[4] > 0.9, "Top class should dominate ergodic distribution"


def test_clmarkov_matchmat(csiss):
    from Markov import ClMarkov
    cm = ClMarkov(csiss['income'])
    assert hasattr(cm, 'matchMat')
    # matchMat keys are (i,j) tuples; (0,0) should have region and time sets
    key = (0, 0)
    assert key in cm.matchMat
    regions, times = cm.matchMat[key]
    assert len(regions) > 0


def test_spmarkov_shapes(csiss):
    from Markov import SpMarkov
    sm = SpMarkov(csiss['income'], csiss['wsp'])
    assert sm.transMat.shape == (5, 5, 5)
    assert sm.pMat.shape == (5, 5, 5)
    assert sm.edists.shape == (5, 5)


def test_spmarkov_edists_rowsums(csiss):
    from Markov import SpMarkov
    sm = SpMarkov(csiss['income'], csiss['wsp'])
    np.testing.assert_allclose(sm.edists.sum(axis=1), 1.0, rtol=1e-10)
