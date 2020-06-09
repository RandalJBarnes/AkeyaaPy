"""Test akeyaa.archive.py"""

from akeyaa.archive import saveme, loadme


def test_archive():
    """Test saveme and loadme."""

    venue, settings, results = loadme('AkeyaaTest.pklz')

#    assert venue.__class__ == venues.Frame
    assert venue.name == 'Frame'
    assert venue.xmin == 503000
    assert venue.xmax == 504000
    assert venue.ymin == 5011500
    assert venue.ymax == 5012500

#    assert settings.__class__ == parameters.Parameters
    assert settings.aquifers is None
    assert settings.method == 'TUKEY'
    assert settings.radius == 500
    assert settings.required == 25
    assert settings.spacing == 200
