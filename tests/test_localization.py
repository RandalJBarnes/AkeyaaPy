"""


Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
25 May 2020
"""

import os

from localization import CWILOC, CTYLOC, TRSLOC, WBDLOC


# -----------------------------------------------------------------------------
def test_localization():
    assert(os.path.isdir(CWILOC))
    assert(os.path.isdir(CTYLOC))
    assert(os.path.isdir(TRSLOC))
    assert(os.path.isdir(WBDLOC))