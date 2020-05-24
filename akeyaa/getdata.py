"""
A set of functions to retrieve data from specific ArgGIS Pro .gdb files.

Functions
---------

----- get data -----
get_well_data({aquifer_list=None})
    Return a list of well data for selectable wells from the specified
    aquifer(s). All wells within the state are considered.

get_well_data_by_polygon(poly, aquifer_list=None)
    Return a list of well data for selectable wells from the specified
    aquifer(s). Only wells within the specified polygon are considered.

get_well_data_by_county(cty_code, {aquifer_list=None})
    Return a list of well data for selectable wells from the specified
    aquifer(s). Only wells within the specified county are considered.

get_well_data_by_township_and_range(twnshp, rng, aquifer_list=None)
    Return a list of well data for selectable wells from the specified
    aquifer(s). Only wells within the specified township are considered.

----- county -----
get_county_code(cty_abbr)
    Get the county code from the county abbreviation.

get_county_abbr(cty_code)
    Get the county abbreviation from the county code.

get_county_name(cty_abbr)
    Get the county name from the county abbreviation.

get_county_polygon(cty_abbr)
    Get the county polygon from the county abbreviation.

----- township, range, section -----
get_township_polygon(twnshp, rng)
    Get the township polygon.

get_section_polygon(twnshp, rng, sctn)
    Get the section polygon.

----- watershed -----
get_watershed_name(wtrs_code)
    Get the watershed name from the watershed code (HUC10).

get_watershed_code(wtrs_name)
    Get the watershed code (HUC10) from the watershed name.

get_watershed_polygon(wtrs_code)
    Get the watershed polygon from the watershed code (HUC10).

Notes
-----
o   Make sure that the localization file is present, correct, and complete.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
24 May 2020
"""

import arcpy
from pyproj import CRS, Transformer

from localization import CTYLOC, CWILOC, TRSLOC, WBDLOC


# Feature classes of interest.
TWNRNG = TRSLOC + r'\tr'
SECTIONS = TRSLOC + r'\trs'
COUNTIES = CTYLOC + r'\mn_county_boundaries'
WELLS = CWILOC + r'\allwells'
SWLS = CWILOC + r'\C5WL'
WTRSHD = WBDLOC + r'\WBDHU10'

# The attributes to include in well data.
ATTRIBUTES = ['allwells.SHAPE',
              'C5WL.MEAS_ELEV',
              'C5WL.MEAS_DATE',
              'allwells.AQUIFER',
              'allwells.RELATEID']

# Common selection criteria: must have a recorded SWL, must have an identified
# aquifer, and must be located.
WHERE = ("(C5WL.MEAS_ELEV is not NULL) AND "
         "(allwells.AQUIFER is not NULL) AND "
         "(allwells.UTME is not NULL) AND "
         "(allwells.UTMN is not NULL)")


# -----------------------------------------------------------------------------
class Error(Exception):
    """
    The base exception for the module.
    """


class NotFoundError(Error):
    """
    Requested item was not found.
    """


class ArgumentError(Error):
    """
    Invalid argument.
    """


# -----------------------------------------------------------------------------
def get_well_data(aquifer_list=None):
    """
    Return a list of well data for selectable wells from the specified
    aquifer(s). All wells within the state are considered.

    Arguments
    ---------
    aquifer_list : list (optional)
        List of 4-character aquifer abbreviation strings. If none, then all
        available aquifers will be included.

    Returns
    -------
    welldata : list
        Each element in the list is a tuple containing all of the attributes
        included in the ATTRIBUTES constant (see above).

    """
    where = WHERE

    if aquifer_list is not None:
        if isinstance(aquifer_list, list):
            where += " AND ("

            for i, code in enumerate(aquifer_list):
                if i != 0:
                    where += " OR "
                where += "(allwells.AQUIFER = '{}')".format(code)
            where += ")"
        else:
            raise ArgumentError

    joined_table = arcpy.AddJoin_management(WELLS, 'RELATEID', SWLS, 'RELATEID', False)

    welldata = []
    with arcpy.da.SearchCursor(joined_table, ATTRIBUTES, where) as cursor:
        for row in cursor:
            welldata.append(row)

    return welldata


# -----------------------------------------------------------------------------
def get_well_data_by_polygon(poly, aquifer_list=None):
    """
    Return a list of well data for selectable wells from the specified
    aquifer(s). Only wells within the specified polygon are considered.

    Arguments
    ---------
    poly : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm

    aquifer_list : list (optional)
        List of 4-character aquifer abbreviation strings. If none, then all
        available aquifers will be included.

    Returns
    -------
    welldata : list
        Each element in the list is a tuple containing all of the attributes
        included in the ATTRIBUTES constant (see above).

    """
    where = WHERE

    if aquifer_list is not None:
        if isinstance(aquifer_list, list):
            where += " AND ("

            for i, code in enumerate(aquifer_list):
                if i != 0:
                    where += " OR "
                where += "(allwells.AQUIFER = '{}')".format(code)
            where += ")"
        else:
            raise ArgumentError

    joined_table = arcpy.AddJoin_management(WELLS, 'RELATEID', SWLS, 'RELATEID', False)

    located_wells = arcpy.SelectLayerByLocation_management(
        joined_table,
        select_features=poly,
        overlap_type='WITHIN',
        selection_type='NEW_SELECTION')

    welldata = []
    with arcpy.da.SearchCursor(located_wells, ATTRIBUTES, where) as cursor:
        for row in cursor:
            welldata.append(row)

    return welldata


# -----------------------------------------------------------------------------
def get_well_data_by_county(cty_code, aquifer_list=None):
    """
    Return a list of well data for selectable wells from the specified
    aquifer(s). Only wells within the specified county are considered.

    Arguments
    ---------
    cty_code : int
        A two digit number

    aquifer_list : list (optional)
        List of 4-character aquifer abbreviation strings. If None, then all
        available aquifers will be included.

    Returns
    -------
    welldata : list
        Each element in the list is a tuple containing all of the attributes
        included in the ATTRIBUTES constant (see above).
    """
    where = WHERE

    # Note that the COUNTY_C in allwells is a two character str that
    # contains the county code.
    where += "AND (allwells.COUNTY_C = '{0:02d}')".format(cty_code)

    if aquifer_list is not None:
        if isinstance(aquifer_list, list):
            where += " AND ("

            for i, code in enumerate(aquifer_list):
                if i != 0:
                    where += " OR "
                where += "(allwells.AQUIFER = '{}')".format(code)
            where += ")"
        else:
            raise ArgumentError

    joined_table = arcpy.AddJoin_management(WELLS, 'RELATEID', SWLS, 'RELATEID', False)

    welldata = []
    with arcpy.da.SearchCursor(joined_table, ATTRIBUTES, where) as cursor:
        for row in cursor:
            welldata.append(row)

    return welldata


# -----------------------------------------------------------------------------
def get_well_data_by_township_and_range(twnshp, rng, aquifer_list=None):
    """
    Return a list of well data for selectable wells from the specified
    aquifer(s). Only wells within the specified township are considered.

    Arguments
    ---------
    twnshp : int
        Township number.

    rng : int
        Range number.

    aquifer_list : list (optional)
        List of 4-character aquifer abbreviation strings. If None, then all
        available aquifers will be included.

    Returns
    -------
    welldata : list
        Each element in the list is a tuple containing all of the attributes
        included in the ATTRIBUTES constant (see above).
    """
    where = WHERE

    if isinstance(twnshp, int) and isinstance(rng, int):
        where += "AND (allwells.TOWNSHIP = {0:d}) AND (allwells.RANGE = {1:d})".format(twnshp, rng)
    else:
        raise ArgumentError

    if aquifer_list is not None:
        if isinstance(aquifer_list, list):
            where += " AND ("

            for i, code in enumerate(aquifer_list):
                if i != 0:
                    where += " OR "
                where += "(allwells.AQUIFER = '{}')".format(code)
            where += ")"
        else:
            raise ArgumentError

    joined_table = arcpy.AddJoin_management(WELLS, 'RELATEID', SWLS, 'RELATEID', False)

    welldata = []
    with arcpy.da.SearchCursor(joined_table, ATTRIBUTES, where) as cursor:
        for row in cursor:
            welldata.append(row)

    return welldata


# -----------------------------------------------------------------------------
def get_county_code(cty_abbr):
    """
    Get the county code from the county abbreviation.

    Arguments
    ---------
    cty_abbr : str
        The 4-character county abbreviation string.

    Returns
    -------
    cty_code : int
        Two-digit county code.
    """
    if isinstance(cty_abbr, str) and len(cty_abbr) == 4:
        where = "CTY_ABBR = '{0}'".format(cty_abbr)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(COUNTIES, ['COUN'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_abbr(cty_code):
    """
    Get the county abbreviation from the county code.

    Arguments
    ---------
    cty_code : int
        Two-digit county code.

    Returns
    -------
    cty_abbr : str
        The 4-character county abbreviation string.
    """
    where = "COUN = {}".format(cty_code)

    with arcpy.da.SearchCursor(COUNTIES, ['CTY_ABBR'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_name(cty_abbr):
    """
    Get the county name from the county abbreviation.

    Arguments
    ---------
    cty_abbr : str
        The 4-character county abbreviation string.

    Returns
    -------
    name : str
        The complete official name of the county.
    """
    if isinstance(cty_abbr, str) and len(cty_abbr) == 4:
        where = "CTY_ABBR = '{}'".format(cty_abbr)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(COUNTIES, ['CTY_NAME'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_polygon(cty_abbr):
    """
    Get the county polygon from the county abbreviation.

    Arguments
    ---------
    cty_abbr : str
        The 4-character county abbreviation string.

    Returns
    -------
    poly : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
    """
    if isinstance(cty_abbr, str) and len(cty_abbr) == 4:
        where = "CTY_ABBR = '{}'".format(cty_abbr)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(COUNTIES, ['SHAPE@'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_township_polygon(twnshp, rng):
    """
    Get the township polygon.

    Arguments
    ---------
    twnshp : int
        Township number.

    rng : int
        Range number.

    Returns
    -------
    poly : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
    """
    if isinstance(twnshp, int) and isinstance(rng, int):
        where = "TOWN = {0:d} AND RANG = {1:d}".format(twnshp, rng)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(TWNRNG, ['SHAPE@'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError

# -----------------------------------------------------------------------------
def get_section_polygon(twnshp, rng, sctn):
    """
    Get the section polygon.

    Arguments
    ---------
    twnshp : int
        Township number.

    rng : int
        Range number.

    sctn : int
        Section number.

    Returns
    -------
    poly : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
    """
    if isinstance(twnshp, int) and isinstance(rng, int) and isinstance(sctn, int):
        where = "TOWN = {0:d} AND RANG = {1:d} AND SECT = {2:d}".format(twnshp, rng, sctn)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(SECTIONS, ['SHAPE@'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_watershed_code(wtrs_name):
    """
    Get the watershed code (HUC10) from the watershed name.

    Arguments
    ---------
    wtrshd : str
        The watershed name string.

    Returns
    -------
    wtrs_code : str
        10-digit watershed code as a string.
    """
    if isinstance(wtrs_name, str):
        where = "NAME = '{0}'".format(wtrs_name)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(WTRSHD, ['HUC10'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_watershed_name(wtrs_code):
    """
    Get the watershed name from the watershed code (HUC10).

    Arguments
    ---------
    wtrs_code : str
        10-digit watershed code as a string.

    Returns
    -------
    wtrshd : str
        The watershed name string.
    """
    if isinstance(wtrs_code, str):
        where = "HUC10 = '{0}'".format(wtrs_code)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(WTRSHD, ['NAME'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError

# -----------------------------------------------------------------------------
def get_watershed_polygon(wtrs_code):
    """
    Get the watershed polygon from the watershed code (HUC10).

    Arguments
    ---------
    wtrs_code : str
        10-digit watershed code as a string.

    Returns
    -------
    poly : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm

    Notes
    -----
    o   The watershed polygons in WBD_National_GDB.gdb are stored using
        lat/lon coordinates; more specifically 'GRS 1980' (EPSG:7019),
        which is a precursor of 'WGS 84' (EPSG:4326).

    o   All of the Minnesota State agencies use 'NAD 83 UTM 15N'(EPSG:26915).

    o   This function gets the polygon from WBD_National_GDB.gdb, then
        creates a new polygon with the original EPSG:7019 coordinates
        converted to EPSG:26916 coordinates.

    o   There must be a way to do this conversion within arcpy, but I could
        not figure it out. So this code does the conversion "by hand" using
        the pyproj library.

    o   However, pyproj does not have 'GRS 1980' (EPSG:7019) built in, so
        this code uses 'WGS 84' (EPSG:4326) instead. The differences are
        insignificant for our purposes.
    """
    if isinstance(wtrs_code, str):
        where = "HUC10 = '{0}'".format(wtrs_code)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(WTRSHD, ['SHAPE@'], where) as cursor:
        try:
            poly7019 = cursor.next()[0]
        except StopIteration:
            raise NotFoundError

    # Extract the polygon vertices in EPSG:7019.
    lon7019 = [pnt.X for pnt in poly7019.getPart(0)]
    lat7019 = [pnt.Y for pnt in poly7019.getPart(0)]

    # Convert from EPSG:7019 to EPSG:26915
    crs_utm = CRS.from_user_input(26915)
    crs_latlon = CRS.from_user_input(4326)
    transformer = Transformer.from_crs(crs_latlon, crs_utm)
    x26915, y26915 = transformer.transform(lat7019, lon7019)

    # Create the new arcpy.Polygon.
    xy26915 = list(zip(x26915, y26915))
    array26915 = arcpy.Array([arcpy.Point(pt[0], pt[1]) for pt in xy26915])
    poly = arcpy.Geometry('Polygon', array26915, arcpy.SpatialReference(26915))

    return poly
