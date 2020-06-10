"""ArcGIS Pro/ArcPy isolation.

All calls to ArcGIS Pro/ArcPy, and the interactions with any
ArcGIS Pro/ArcPy data types, are ISOLATED in this module.

get_all_well_data()
    Query arcpy for the welldata from all authorized wells in the state.

get_venue_data(source, what, where)
    Query acrpy for venue data.

get_city_data(name=None, gnis_id=None)
    Return the City venue data.

get_township_data(name=None, gnis_id=None)
    Return the Township venue data.

get_watershed_data(name=None, huc10=None)
    Return the Watershed venue data.

get_subregion_data(name=None, huc8=None)
    Return the Subregion venue data.

get_county_data(name=None, abbr=None, cty_fips=None)
    Return the County venue data.

get_state_data()
    Return the State venue data.

"""
import numpy as np

import pyproj
import arcpy

from akeyaa.localpaths import SOURCE


class Error(Exception):
    """The base exception for the module."""


class VenueNotFoundError(Error):
    """The requested venue was not found in the database."""


class VenueNotUniqueError(Error):
    """The requested venue is not unique in the database."""


class WellNotFoundError(Error):
    """The requested well was not found in the database."""


class WellNotUniqueError(Error):
    """The requested well is not unique in the database."""


# ------------------------------------------------------------------
# ----- Functions that interact directly with ArcGIS Pro/ArcPy -----
# ------------------------------------------------------------------

def get_all_well_data():
    """Query arcpy for the welldata from all authorized wells in the state.

    Returns
    -------
    welldata : list[tuple] ((x, y), z, aquifer, relateid)
        (x, y) : tuple(float, float)
            The x- and y-coordinates in "NAD 83 UTM 15N" (EPSG:26915) [m].

        z : float
            The measured static water level [ft]

        aquifer : str
            The 4-character aquifer abbreviation string, as defined in
            Minnesota Geologic Survey's coding system.

        relateid : str
            The unique 10-digit well number encoded as a string with
            leading zeros.

        For example: ((232372.0, 5377518.0), 964.0, 'QBAA', '0000153720')

    """
    in_table = arcpy.AddJoin_management(
        SOURCE["ALLWELLS"], "RELATEID", SOURCE["C5WL"], "RELATEID", False
    )

    field_names = [
        "allwells.SHAPE",
        "C5WL.MEAS_ELEV",
        "allwells.AQUIFER",
        "allwells.RELATEID",
    ]

    where_clause = (
        "(C5WL.MEAS_ELEV is not NULL) AND "
        "(allwells.AQUIFER is not NULL) AND "
        "(allwells.UTME is not NULL) AND "
        "(allwells.UTMN is not NULL)"
    )

    with arcpy.da.SearchCursor(in_table, field_names, where_clause) as cursor:
        return list(cursor)


def get_venue_data(source, what, where):
    """Query acrpy for civil venue data."""

    results = []
    with arcpy.da.SearchCursor(source, what, where) as cursor:
        for row in cursor:
            results.append(row)

    if len(results) == 0:
        raise VenueNotFoundError(f"{where}")

    if len(results) > 1:
        for row in results:
            print(row[0:2])
        raise VenueNotUniqueError(f"{where}")

    poly = results[0][2]

    x = [pnt.X for pnt in poly.getPart(0)]
    y = [pnt.Y for pnt in poly.getPart(0)]

    if poly.spatialReference.type == "Geographic":
        # Convert lat/lon coordinates, GCS North America 1983 (EPSG:4269),
        # to UTM coordinate, NAD 83 UTM zone 15N (EPSG:26915).
        projector = pyproj.Proj("epsg:26915", preserve_units=False)
        x, y = projector(x, y)

    name = results[0][0]
    code = results[0][1]
    vertices = np.column_stack((x, y))

    return (name, code, vertices)


# --------------------------------------------------------------------
# ----- Functions that interact indirectly with ArcGIS Pro/ArcPy -----
# --------------------------------------------------------------------

def get_city_data(*, name=None, gnis_id=None):
    """Return the City venue data."""

    source = SOURCE["CITY"]
    what = ["NAME", "GNIS_ID", "SHAPE@"]
    where = "(CTU_Type = 'CITY')"

    if name is not None:
        where += f" AND (NAME = '{name}')"

    if gnis_id is not None:
        where += f" AND (GNIS_ID = '{gnis_id}')"

    return get_venue_data(source, what, where)


def get_township_data(*, name=None, gnis_id=None):
    """Return the Township venue data."""

    source = SOURCE["TOWNSHIP"]
    what = ["NAME", "GNIS_ID", "SHAPE@"]
    where = "(CTU_Type = 'TOWNSHIP')"

    if name is not None:
        where += f" AND (NAME = '{name}')"

    if gnis_id is not None:
        where += f" AND (GNIS_ID = '{gnis_id}')"

    return get_venue_data(source, what, where)


def get_county_data(*, name=None, abbr=None, cty_fips=None):
    """Return the County venue data."""

    source = SOURCE["COUNTY"]
    what = ["CTY_NAME", "CTY_FIPS", "SHAPE@"]
    where = ""

    if name is not None:
        where = f"(CTY_NAME = '{name}')"

    if abbr is not None:
        if where:
            where += f" AND (CTY_ABBR = '{abbr}')"
        else:
            where = f"(CTY_ABBR = '{abbr}')"

    if cty_fips is not None:
        if where:
            where += f" AND (CTY_FIPS = '{cty_fips}')"
        else:
            where = f"(CTY_FIPS = '{cty_fips}')"

    return get_venue_data(source, what, where)


def get_watershed_data(*, name=None, huc10=None):
    """Return the Watershed venue data."""

    source = SOURCE["WATERSHED"]
    what = ["NAME", "HUC10", "SHAPE@"]
    where = "(STATES LIKE '%MN%')"

    if name is not None:
        where += f" AND (NAME = '{name}')"

    if huc10 is not None:
        where += f" AND (HUC10 = '{huc10}')"

    return get_venue_data(source, what, where)


def get_subregion_data(*, name=None, huc8=None):
    """Return the Subregion venue data."""

    source = SOURCE["SUBREGION"]
    what = ["NAME", "HUC8", "SHAPE@"]
    where = "(STATES LIKE '%MN%')"

    if name is not None:
        where += f"AND (NAME = '{name}')"

    if huc8 is not None:
        where += f"AND (HUC8 = '{huc8}')"

    return get_venue_data(source, what, where)


def get_state_data():
    """Return the State venue data."""

    source = SOURCE["STATE"]
    what = ["STATE_NAME", "STATE_FIPS_CODE", "SHAPE@"]
    where = "STATE_NAME = 'Minnesota'"

    return get_venue_data(source, what, where)
