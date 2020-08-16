"""Test akeyaa.paramters.py"""
import pytest

from akeyaa.hold.parameters import Parameters
from akeyaa.hold.parameters import (
    DEFAULT_AQUIFERS,
    DEFAULT_AFTER,
    DEFAULT_BEFORE,
    DEFAULT_METHOD,
    DEFAULT_RADIUS,
    DEFAULT_REQUIRED,
    DEFAULT_SPACING,
)


def test_parameters():
    """Test the properties."""
    p = Parameters()
    assert p.aquifers == DEFAULT_AQUIFERS
    assert p.after == DEFAULT_AFTER
    assert p.before == DEFAULT_BEFORE
    assert p.method == DEFAULT_METHOD
    assert p.radius == DEFAULT_RADIUS
    assert p.required == DEFAULT_REQUIRED
    assert p.spacing == DEFAULT_SPACING

    with pytest.raises(ValueError):
        Parameters(aquifers=["ABCD"])

    with pytest.raises(ValueError):
        Parameters(after='01 January 1990')

    with pytest.raises(ValueError):
        Parameters(before='01/01/1990')

    with pytest.raises(ValueError):
        Parameters(radius=-1)

    with pytest.raises(ValueError):
        Parameters(method="NO METHOD")

    with pytest.raises(ValueError):
        Parameters(radius=-1)

    with pytest.raises(ValueError):
        Parameters(required=5)

    with pytest.raises(ValueError):
        Parameters(spacing=0)
