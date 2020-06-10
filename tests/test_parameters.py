"""Test akeyaa.paramters.py"""
import pytest

from akeyaa.parameters import Parameters
from akeyaa.parameters import (
    DEFAULT_AQUIFERS,
    DEFAULT_METHOD,
    DEFAULT_RADIUS,
    DEFAULT_REQUIRED,
    DEFAULT_SPACING,
)


def test_parameters():
    """Test the properties."""
    p = Parameters()
    assert p.aquifers == DEFAULT_AQUIFERS
    assert p.method == DEFAULT_METHOD
    assert p.radius == DEFAULT_RADIUS
    assert p.required == DEFAULT_REQUIRED
    assert p.spacing == DEFAULT_SPACING

    with pytest.raises(ValueError):
        Parameters(aquifers=["ABCD"])

    with pytest.raises(ValueError):
        Parameters(method="NO METHOD")

    with pytest.raises(ValueError):
        Parameters(radius=-1)

    with pytest.raises(ValueError):
        Parameters(required=5)

    with pytest.raises(ValueError):
        Parameters(spacing=0)
