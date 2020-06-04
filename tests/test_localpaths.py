"""


Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
04 June 2020

"""

import os

import localpaths as loc


# -----------------------------------------------------------------------------
def test_localization():
    assert(os.path.isdir(loc.CWIGDB))
    assert(os.path.isdir(loc.CTYGDB))
    assert(os.path.isdir(loc.STAGDB))
    assert(os.path.isdir(loc.CTUGDB))
    assert(os.path.isdir(loc.WBDGDB))