"""


Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
27 May 2020

"""

import os

import localization as loc


# -----------------------------------------------------------------------------
def test_localization():
    assert(os.path.isdir(loc.CWILOC))
    assert(os.path.isdir(loc.CTYLOC))
    assert(os.path.isdir(loc.STALOC))
    assert(os.path.isdir(loc.TRSLOC))
    assert(os.path.isdir(loc.WBDLOC))