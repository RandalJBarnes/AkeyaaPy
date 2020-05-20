"""
A set of functions to retrieve data from specific ArgGIS Pro .gdb files.

Functions
---------
get_well_data({aquifer_list=None})
    Get the well data across the state from the specified aquifer(s).

get_well_data_by_county(cty_code, {aquifer_list=None})
    Get the well data across the specified county.

get_well_data_by_township_and_range(twnshp, rng)
    Get the well data across the specified township.

get_county_code(cty_abbr)
    Get the county code from the county abbreviation.

get_county_abbr(cty_code)
    Get the county abbreviation from the county code.

get_county_name(cty)
    Get the county name from the county code or county abbreviation.

get_county_polygon(cty)
    Get the county polygon from the county code or county abbreviation.

get_township_polygon(twnshp, rng)
    Get the township polygon.

get_section_polygon(twnshp, rng, sctn)
    Get the section polygon.

Notes
-----
o   The localization file must be correct for the installation.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
20 May 2020
"""

import arcpy
from localization import CTYLOC, CWILOC, TRSLOC


# Feature classes of interest.
TWNRNG = TRSLOC + r'\tr'
SECTIONS = TRSLOC + r'\trs'
COUNTIES = CTYLOC + r'\mn_county_boundaries'
WELLS = CWILOC + r'\allwells'
SWLS = CWILOC + r'\C5WL'

# The attributes to include in well data.
ATTRIBUTES = ['allwells.SHAPE',
              'C5WL.MEAS_ELEV',
              'C5WL.MEAS_DATE',
              'allwells.AQUIFER',
              'allwells.RELATEID']

# Common selection criteria.
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
    Get the well data across the state from the specified aquifer(s).

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
def get_well_data_by_county(cty_code, aquifer_list=None):
    """
    Get the well data across the specified county.

    Arguments
    ---------
    cty_abbr : str
        The 4-character county abbreviation string.

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

    if isinstance(cty_code, int) and (cty_code > 0):
        where += "AND (allwells.COUNTY_C = '{0:2d}')".format(cty_code)
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
def get_well_data_by_township_and_range(twnshp, rng, aquifer_list=None):
    """
    Get the well data across the specified township.

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
        where = "CTY_ABBR = '{}'".format(cty_abbr)
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
    if isinstance(cty_code, int) and (cty_code > 0):
        where = "COUN = {}".format(cty_code)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(COUNTIES, ['CTY_ABBR'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_name(cty):
    """
    Get the county name from the county code or county abbreviation.

    Arguments
    ---------
    cty : either ...
        cty_code : int
            Two-digit county code.

        cty_abbr : str
            The 4-character county abbreviation string.

    Returns
    -------
    name : str
        The complete official name of the county.
    """
    if isinstance(cty, int) and (cty > 0):
        where = "COUN = {}".format(cty)
    elif isinstance(cty, str) and len(cty) == 4:
        where = "CTY_ABBR = '{}'".format(cty)
    else:
        raise ArgumentError

    with arcpy.da.SearchCursor(COUNTIES, ['CTY_NAME'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_polygon(cty):
    """
    Get the county polygon from the county code or county abbreviation.

    Arguments
    ---------
    cty : either ...
        cty_code : int
            Two-digit county code.

        cty_abbr : str
            The 4-character county abbreviation string.

    Returns
    -------
    poly : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
    """
    if isinstance(cty, int) and (cty > 0):
        where = "COUN = {}".format(cty)
    elif isinstance(cty, str) and len(cty) == 4:
        where = "CTY_ABBR = '{}'".format(cty)
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
