"""Shared fixtures for STARS test suite."""
import sys
import os
import pytest
import numpy as np

# Run all tests from the data directory so csiss dataset can be found
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'stars', 'data')
STARS_DIR = os.path.join(os.path.dirname(__file__), '..', 'stars')

sys.path.insert(0, os.path.abspath(STARS_DIR))


@pytest.fixture(scope='session')
def csiss():
    """Load the csiss STARS project (income, bea region, weights)."""
    orig_dir = os.getcwd()
    os.chdir(DATA_DIR)
    try:
        from stars import Project
        from Data import spGalMatrix
        s = Project('s')
        s.ReadData('csiss')
        income = s.getVariable('pcincome')
        region = s.getVariable('bea')
        with open('states48.gal', 'r') as fh:
            galinfo = list(map(int, fh.read().split()))
        wsp = spGalMatrix('wsp', galinfo)
        yield {'income': income, 'region': region, 'wsp': wsp, 'project': s}
    finally:
        os.chdir(orig_dir)
