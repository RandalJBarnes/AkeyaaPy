import os

import localpaths as loc


# -----------------------------------------------------------------------------
def test_localization():
    assert(os.path.isdir(loc.CWIGDB))
    assert(os.path.isdir(loc.CTYGDB))
    assert(os.path.isdir(loc.STAGDB))
    assert(os.path.isdir(loc.CTUGDB))
    assert(os.path.isdir(loc.WBDGDB))