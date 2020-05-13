"""
Test the countydata.py functions.

Author
------
    Dr. Randal J. Barnes
    Department of Civil, Environmental, and Geo- Engineering
    University of Minnesota

Version
-------
    13 May 2020
"""

import numpy as np
import pytest

import arcpy

from akeyaa.getdata import get_county_code, get_county_name, get_county_polygon
from akeyaa.getdata import ArgumentError, NotFoundError


# -----------------------------------------------------------------------------
def test_get_county_code():
    assert(get_county_code('ISAN') == 30)
    assert(get_county_code('WASH') == 82)

    with pytest.raises(ArgumentError):
        get_county_code(30)

    with pytest.raises(ArgumentError):
        get_county_code('Isanti')

    with pytest.raises(NotFoundError):
        get_county_code('FRED')


# -----------------------------------------------------------------------------
def test_get_county_name():
    assert(get_county_name(13)=='Chisago')
    assert(get_county_name('WASH')=='Washington')

    with pytest.raises(ArgumentError):
        get_county_name('Isanti')

    with pytest.raises(ArgumentError):
        get_county_name(-1)

    with pytest.raises(NotFoundError):
        get_county_name(123)

    with pytest.raises(NotFoundError):
        get_county_name('FRED')


# -----------------------------------------------------------------------------
def test_get_county_polygon():
    p = get_county_polygon(30)
    assert(isinstance(p, arcpy.Polygon))
    assert(np.isclose(p.area, 1168461203.4077861))

    with pytest.raises(ArgumentError):
        get_county_polygon('Isanti')

    with pytest.raises(ArgumentError):
        get_county_polygon(-1)

    with pytest.raises(NotFoundError):
        get_county_polygon(123)

    with pytest.raises(NotFoundError):
        get_county_polygon('FRED')


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # execute only if run as a script
    test_get_county_code()
    test_get_county_name()
    test_get_county_polygon()