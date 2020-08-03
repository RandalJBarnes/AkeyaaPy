"""ArcGIS Pro/ArcPy isolation.

All calls to ArcGIS Pro/ArcPy, and the interactions with any
ArcGIS Pro/ArcPy data types, are ISOLATED in this module.

get_all_well_data()
    Query arcpy for the welldata from all authorized wells in the state.

_get_venue_data(source, what, where)
    Query acrpy for venue data. This is intended as a private method.

get_city_list()
    Return list of all cities and gnis_ids

get_township_list()
    Return list of all townships and gnis_ids

get_county_list()
    Return list of all cities and cty_fips

get_watershed_list()
    Return list of all watersheds and HUC10s

get_subregion_list()
    Return list of all subregions and HUC8s

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

See Also
--------
akeyaa.venues, akeyaa.wells

"""
import numpy as np
import pyproj
import arcpy

from akeyaa.localpaths import CTUGDB, CTYGDB, WBDGDB, STAGDB, CWIGDB

__author__ = "Randal J Barnes"
__version__ = "24 July 2020"


# The location details of specific feature classes.
SOURCE = {
    "CITY"      : CTUGDB + r"\city_township_unorg",     # City boundaries
    "TOWNSHIP"  : CTUGDB + r"\city_township_unorg",     # Township boundaries
    "COUNTY"    : CTYGDB + r"\mn_county_boundaries",    # County boundaries
    "WATERSHED" : WBDGDB + r"\WBDHU10",                 # Watershed boundaries
    "SUBREGION" : WBDGDB + r"\WBDHU8",                  # Subregion boundaries
    "STATE"     : STAGDB + r"\Boundaries_of_Minnesota", # MN state boundary
    "ALLWELLS"  : CWIGDB + r"\allwells",                # MN county well index
    "C5WL"      : CWIGDB + r"\C5WL",                    # MN static water levels
}


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
        "C5WL.MEAS_DATE",
    ]

    where_clause = (
        "(C5WL.MEAS_ELEV is not NULL) AND "
        "(allwells.AQUIFER is not NULL) AND "
        "(allwells.UTME is not NULL) AND "
        "(allwells.UTMN is not NULL)"
    )

    with arcpy.da.SearchCursor(in_table, field_names, where_clause) as cursor:
        return list(cursor)


def _get_venue_data(source, what, where):
    """Query acrpy for venue data. This is intended as a private method.

    Query various .gdb for the names, unique codes, and boundary polygon of
    a political division or administrative region: for example: a ``City``,
    ``County``, or ``Watershed``.

    If the boundary polygon is given in lat/lon, the coordinates are converted
    into NAD 83 UTM zone 15N (EPSG:26915).

    Prameters
    ---------
    source : str
        The complete, localized, path to the data, including the feature class.

    what : list[str]
        A list of field names to extract.

    where : str
        The detailed where SQL-type where clause.

    Returns
    -------
    name : str
        The venue name as stored in the .gdb.

    code : str, int
        The unique code (str or int) associated with the venue type.

    vertices : list[(x, y)]
        The vertices of the boundary polygon as stored in the .gdb.

    Raises
    ------
    VenueNotFoundError
    VenueNotUniqueError

    """
    results = []
    with arcpy.da.SearchCursor(source, what, where) as cursor:
        for row in cursor:
            results.append(row)

    if len(results) == 0:
        raise VenueNotFoundError(f"{where}")

    if len(results) > 1:
        message = f"{where}"
        for row in results:
            message += f"\n {row[0:2]}"
        raise VenueNotUniqueError(message)

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
def get_city_list():
    source = SOURCE["CITY"]
    what = ["NAME", "GNIS_ID"]
    where = "(CTU_Type = 'CITY')"

    city_list = []
    with arcpy.da.SearchCursor(source, what, where) as cursor:
        for row in cursor:
            city_list.append(row)
    return city_list

def get_township_list():
    source = SOURCE["TOWNSHIP"]
    what = ["NAME", "GNIS_ID"]
    where = "(CTU_Type = 'TOWNSHIP')"

    township_list = []
    with arcpy.da.SearchCursor(source, what, where) as cursor:
        for row in cursor:
            township_list.append(row)
    return township_list

def get_county_list():
    source = SOURCE["COUNTY"]
    what = ["CTY_NAME", "CTY_FIPS"]
    where = ""

    county_list = []
    with arcpy.da.SearchCursor(source, what, where) as cursor:
        for row in cursor:
            county_list.append(row)
    return county_list

def get_watershed_list():
    source = SOURCE["WATERSHED"]
    what = ["NAME", "HUC10", "SHAPE@"]
    where = "(STATES LIKE '%MN%')"

    watershed_list = []
    with arcpy.da.SearchCursor(source, what, where) as cursor:
        for row in cursor:
            watershed_list.append(row)
    return watershed_list

def get_subregion_list():
    source = SOURCE["SUBREGION"]
    what = ["NAME", "HUC8", "SHAPE@"]
    where = "(STATES LIKE '%MN%')"

    subregion_list = []
    with arcpy.da.SearchCursor(source, what, where) as cursor:
        for row in cursor:
            subregion_list.append(row)
    return subregion_list


# --------------------------------------------------------------------
# ----- Functions that interact indirectly with ArcGIS Pro/ArcPy -----
# --------------------------------------------------------------------

def get_city_data(*, name=None, gnis_id=None):
    """Return the City venue data.

    Parameters
    ----------
    All arguments are key-word ONLY.

    name : str
        The city name, as stored in the *city_township_unorg* feature
        class.

    gnis_id : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

    Notes
    -----
    The `name`, the `gnis_id`, or both can be specified. The `name` is not
    unique, whereas the `gnis_id` is.

    If only the `name` is specified and it is not unique a VenueNotUniqueError
    is raised. If the `name`, the `gnis_id`, or the combination of both cannot
    be found a VenueNotFoundError is raised.

    """
    source = SOURCE["CITY"]
    what = ["NAME", "GNIS_ID", "SHAPE@"]
    where = "(CTU_Type = 'CITY')"

    if name is not None:
        where += f" AND (NAME = '{name}')"

    if gnis_id is not None:
        where += f" AND (GNIS_ID = '{gnis_id}')"

    return _get_venue_data(source, what, where)


def get_township_data(*, name=None, gnis_id=None):
    """Return the Township venue data.

    Parameters
    ----------
    All arguments are key-word ONLY.

    name : str
        The township name, as stored in the *city_township_unorg* feature
        class.

    gnis_id : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

    Notes
    -----
    The `name`, the `gnis_id`, or both can be specified. The `name` is not
    unique, whereas the `gnis_id` is.

    If only the `name` is specified and it is not unique a VenueNotUniqueError
    is raised. If the `name`, the `gnis_id`, or the combination of both cannot
    be found a VenueNotFoundError is raised.

    """
    source = SOURCE["TOWNSHIP"]
    what = ["NAME", "GNIS_ID", "SHAPE@"]
    where = "(CTU_Type = 'TOWNSHIP')"

    if name is not None:
        where += f" AND (NAME = '{name}')"

    if gnis_id is not None:
        where += f" AND (GNIS_ID = '{gnis_id}')"

    return _get_venue_data(source, what, where)


def get_county_data(*, name=None, abbr=None, cty_fips=None):
    """Return the County venue data.

    Parameters
    ----------
    All arguments are key-word ONLY.

    name : str
        The county name, as stored in the *mn_county_boundaries* feature
        class.

    abbr : str
        The 4-character county name abbreviation, as stored in the
        *mn_county_boundaries* feature class.

    cty_fips : int
        The unique 5-digit Federal Information Processing Standards code
        (FIPS), without the initial 2 digits state code.

    Notes
    -----
    The `name`, 'abbr', `gnis_id`, or any combination can be specified.
    The `name` is not unique, whereas the `abbr` and `cty_fips` are.

    If only the `name` is specified and it is not unique a VenueNotUniqueError
    is raised. If the `name`, `abbr`, `cty_fips`, or a combination cannot
    be found a VenueNotFoundError is raised.

    """
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

    return _get_venue_data(source, what, where)


def get_watershed_data(*, name=None, huc10=None):
    """Return the Watershed venue data.

    Parameters
    ----------
    All arguments are key-word ONLY.

    name : str
        The watershed name, as stored in the *WBDHU10* feature class.

    huc10 : str
        The unique 10-digit hydrologic unit code (HUC10) encoded as a
        string.

    Notes
    -----
    The `name`, the `huc10`, or both can be specified. The `name` is not
    unique, whereas the `huc10` is.

    If only the `name` is specified and it is not unique within the state
    a VenueNotUniqueError is raised. If the `name`, the `huc10`, or the
    combination of both cannot be found a VenueNotFoundError is raised.

    """
    source = SOURCE["WATERSHED"]
    what = ["NAME", "HUC10", "SHAPE@"]
    where = "(STATES LIKE '%MN%')"

    if name is not None:
        where += f" AND (NAME = '{name}')"

    if huc10 is not None:
        where += f" AND (HUC10 = '{huc10}')"

    return _get_venue_data(source, what, where)


def get_subregion_data(*, name=None, huc8=None):
    """Return the Subregion venue data.

    Parameters
    ----------
    All arguments are key-word ONLY.

    name : str
        The watershed name, as stored in the *WBDHU10* feature class.

    huc8 : str
        The unique 8-digit hydrologic unit code (HUC8) encoded as a string.

    Notes
    -----
    The `name`, the `huc8`, or both can be specified. The `name` is not
    unique, whereas the `huc8` is.

    If only the `name` is specified and it is not unique within the state
    a VenueNotUniqueError is raised. If the `name`, the `huc8`, or the
    combination of both cannot be found a VenueNotFoundError is raised.

    """
    source = SOURCE["SUBREGION"]
    what = ["NAME", "HUC8", "SHAPE@"]
    where = "(STATES LIKE '%MN%')"

    if name is not None:
        where += f"AND (NAME = '{name}')"

    if huc8 is not None:
        where += f"AND (HUC8 = '{huc8}')"

    return _get_venue_data(source, what, where)


def get_state_data():
    """Return the State venue data."""

    source = SOURCE["STATE"]
    what = ["STATE_NAME", "STATE_FIPS_CODE", "SHAPE@"]
    where = "STATE_NAME = 'Minnesota'"

    return _get_venue_data(source, what, where)
