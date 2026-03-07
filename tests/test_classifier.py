"""Tests for classifier.py (Phase 1f) and pdf.zprob (Phase 1b)."""
import numpy as np
import pytest


def test_equal_width_bins(csiss):
    """equalWidth via mapclassify.EqualInterval matches expected bin edges."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'stars'))
    from classifier import Classifier
    x = np.asarray(csiss['income'][:, 0]).flatten()
    c = Classifier(x, method='equalWidth', nBins=5)
    assert len(c.bins) == 5
    # Bins should span the data range in equal steps
    w = (x.max() - x.min()) / 5
    np.testing.assert_allclose(c.bins[-1], x.max(), rtol=1e-6)
    np.testing.assert_allclose(c.bins[1] - c.bins[0], w, rtol=1e-6)


def test_equal_width_bin_counts(csiss):
    from classifier import Classifier
    x = np.asarray(csiss['income'][:, 0]).flatten()
    c = Classifier(x, method='equalWidth', nBins=5)
    assert sum(c.binCounts) == len(x)


def test_zprob_scalar():
    """pdf.zprob matches scipy.stats.norm.cdf."""
    from pdf import zprob
    from scipy.stats import norm
    for z in [-3.0, -1.96, 0.0, 1.96, 3.0]:
        np.testing.assert_allclose(zprob(z), norm.cdf(z), rtol=1e-10)


def test_zprob_symmetry():
    from pdf import zprob
    np.testing.assert_allclose(zprob(1.0) + zprob(-1.0), 1.0, rtol=1e-10)


def test_zprob_at_zero():
    from pdf import zprob
    np.testing.assert_allclose(zprob(0.0), 0.5, rtol=1e-10)
