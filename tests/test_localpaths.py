"""Test akeyaa.localpaths.py"""
import os

import akeyaa.localpaths as loc


# -----------------------------------------------------------------------------
def test_localization():
    """Test necessary .gbd folders are where the are supposed to be."""
    assert os.path.isdir(loc.CWIGDB)
    assert os.path.isdir(loc.CTYGDB)
    assert os.path.isdir(loc.STAGDB)
    assert os.path.isdir(loc.CTUGDB)
    assert os.path.isdir(loc.WBDGDB)
    