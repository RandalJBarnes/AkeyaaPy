"""All calls to ArcGIS Pro/ArcPy, and the interactions with any
ArcGIS Pro/ArcPy data types, are ISOLATED in this module.

Functions
---------

----- Functions that interact directly with ArcGIS Pro/ArcPy -----

get_all_well_data()
    Query arcpy for the welldata from all authorized wells in the state.

get_well_data_by_polygon(polygon)
    Query arcpy for the welldata from all authorized wells in the polygon.

get_venue_data(source, what, where)
    Query acrpy for venue data.

----- Functions that interact indirectly with ArcGIS Pro/ArcPy -----

get_city_data(*, name=None, gnis_id=None ):
    Return the City venue data.

get_township_data(*, name=None, gnis_id=None)
    Return the Township venue data.

get_subregion_data(*, name=None, huc8=None)
    Return the Subregion venue data.

get_county_data(*, name=None, abbr=None, cty_fips=None)
    Return the County venue data.

get_state_data()
    Return the State venue data.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
03 June 2020
"""

import numpy as np

import pyproj
import arcpy

from geometry import Polygon
from localpaths import SOURCE


# -----------------------------------------------------------------------------
# The attributes to be include in the arcpy.da.SearchCursor when retrieving
# <welldata> from the ArcGIS Pro/ArcPy .gdb.  By design, this is the one
# place where this is defined.
#
# As used multiple places in this module, the code for setting up <welldata>
# includes:
#
#   [(x, y, z, aq) for (x, y), z, aq in cursor]
#
# If the required attributes to be included in <welldata> change, then these
# few lines of code will need to be updated to reflect the change.
ATTRIBUTES = ["allwells.SHAPE",
              "C5WL.MEAS_ELEV",
              "allwells.AQUIFER"]

# -----------------------------------------------------------------------------
# Wells that satisfy all of these criteria are called "authorized wells".
# These include: must have at least one recorded static water level (SWL),
# must have an identified aquifer, and must be located.
WHERE = (
        "(C5WL.MEAS_ELEV is not NULL) AND "
        "(allwells.AQUIFER is not NULL) AND "
        "(allwells.UTME is not NULL) AND "
        "(allwells.UTMN is not NULL)"
        )

# -----------------------------------------------------------------------------
# This is a list of all state combinations in the USGS hydrologic databases
# that include 'MN'. This is a klude to cover for arcpy's weak SQL tools.
ALL_STATES = ("("
        "(STATES = 'CN,MI,MN,WI') OR "
        "(STATES = 'CN,MN') OR "
        "(STATES = 'CN,MN,ND') OR "
        "(STATES = 'IA,MN') OR "
        "(STATES = 'IA,MN,NE,SD') OR "
        "(STATES = 'IA,MN,SD') OR "
        "(STATES = 'IA,MN,WI') OR "
        "(STATES = 'MN') OR "
        "(STATES = 'MN,ND') OR "
        "(STATES = 'MN,ND,SD') OR "
        "(STATES = 'MN,SD') OR "
        "(STATES = 'MN,WI'))")


# -----------------------------------------------------------------------------
class Error(Exception):
    """The base exception for the module. """

class VenueNotFoundError(Error):
    """The requested venue was not found in the database. """

class VenueNotUniqueError(Error):
    """The requested venue is not unique in the database. """


# ------------------------------------------------------------------
# ----- Functions that interact directly with ArcGIS Pro/ArcPy -----
# ------------------------------------------------------------------

# -----------------------------------------------------------------------------
def get_all_well_data():
    """Query arcpy for the welldata from all authorized wells in the state.

    Returns
    -------
    welldata : list of tuples (x, y, z, aquifer) where
        x : float
            The well x-coordinates in "NAD 83 UTM zone 15N" (EPSG:26915) [m].

        y : float
            The well y-coordinates in "NAD 83 UTM zone 15N" (EPSG:26915) [m].

        z : float
            The measured static water level [ft]

        aquifer : str
            The 4-character aquifer abbreviation string, as defined in
            Minnesota Geologic Survey's coding system.
    """

    ALLWELLS = SOURCE['ALLWELLS']
    C5WL = SOURCE['C5WL']

    table = arcpy.AddJoin_management(ALLWELLS, "RELATEID", C5WL, "RELATEID", False)
    with arcpy.da.SearchCursor(table, ATTRIBUTES, WHERE) as cursor:
        welldata = [(x, y, z, aq) for (x, y), z, aq in cursor]
    return welldata


# -----------------------------------------------------------------------------
def get_well_data_by_polygon(polygon):
    """Query arcpy for the welldata from all authorized wells in the polygon.

    Parameters
    ----------
    polygon : geometry.Polygon
        The geographic focus of the query.

    Returns
    -------
    welldata : list of tuples (x, y, z, aquifer) where
        x : float
            The well x-coordinates in "NAD 83 UTM zone 15N" (EPSG:26915) [m].

        y : float
            The well y-coordinates in "NAD 83 UTM zone 15N" (EPSG:26915) [m].

        z : float
            The measured static water level [ft]

        aquifer : str
            The 4-character aquifer abbreviation string, as defined in
            Minnesota Geologic Survey's coding system.
    """

    ALLWELLS = SOURCE['ALLWELLS']
    C5WL = SOURCE['C5WL']

    table = arcpy.AddJoin_management(ALLWELLS, "RELATEID", C5WL, "RELATEID", False)
    located_wells = arcpy.SelectLayerByLocation_management(
            table,
            select_features=polygon,
            overlap_type="WITHIN",
            selection_type="NEW_SELECTION")
    with arcpy.da.SearchCursor(located_wells, ATTRIBUTES, WHERE) as cursor:
        welldata = [(x, y, z, aq) for (x, y), z, aq in cursor]
    return welldata


# -----------------------------------------------------------------------------
def get_venue_data(source, what, where):
    """Query acrpy for venue data."""

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
    polygon = Polygon(np.column_stack((x, y)))

    return (name, code, polygon)


# --------------------------------------------------------------------
# ----- Functions that interact indirectly with ArcGIS Pro/ArcPy -----
# --------------------------------------------------------------------

# -----------------------------------------------------------------------------
def get_city_data(*, name=None, gnis_id=None ):
    """Return the City venue data."""

    source = SOURCE["CITY"]
    what = ["NAME", "GNIS_ID", "SHAPE@"]
    where = "(CTU_Type = 'CITY')"

    if name is not None:
        where += f" AND (NAME = '{name}')"

    if gnis_id is not None:
        where += f" AND (GNIS_ID = '{gnis_id}')"

    return get_venue_data(source, what, where)


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
def get_watershed_data(*, name=None, huc10=None):
    """Return the Watershed venue data."""

    source = SOURCE["WATERSHED"]
    what = ["NAME", "HUC10", "SHAPE@"]
    where = ALL_STATES

    if name is not None:
        where += f" AND (NAME = '{name}')"

    if huc10 is not None:
        where += f" AND (HUC10 = '{huc10}')"

    return get_venue_data(source, what, where)


# -----------------------------------------------------------------------------
def get_subregion_data(*, name=None, huc8=None):
    """Return the Subregion venue data."""

    source = SOURCE["SUBREGION"]
    what = ["NAME", "HUC8", "SHAPE@"]
    where = ALL_STATES

    if name is not None:
        where += f"AND (NAME = '{name}')"

    if huc8 is not None:
        where += f"AND (HUC8 = '{huc8}')"

    return get_venue_data(source, what, where)


# -----------------------------------------------------------------------------
def get_state_data():
    """Return the State venue data."""

    source = SOURCE["STATE"]
    what = ["STATE_NAME", "STATE_FIPS_CODE", "SHAPE@"]
    where = "STATE_NAME = 'Minnesota'"

    return get_venue_data(source, what, where)
