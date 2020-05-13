"""



Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
13 May 2020
"""

import arcpy

from akeyaa.setlocations import CTYLOC, CWILOC


# Feature classes of interest.
COUNTIES = CTYLOC + r'\mn_county_boundaries'
WELLS = CWILOC + r'\allwells'
SWLS = CWILOC + r'\C5WL'


class Error(Exception):
    pass


class NotFoundError(Error):
    pass


class ArgumentError(Error):
    pass


# -----------------------------------------------------------------------------
def get_county_code(cty):
    if isinstance(cty, str) and len(cty)==4:
        where = "CTY_ABBR = '{}'".format(cty)
    else:
        raise(ArgumentError)

    where = "CTY_ABBR = '{}'".format(cty)
    with arcpy.da.SearchCursor(COUNTIES, ['COUN'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise(NotFoundError)


# -----------------------------------------------------------------------------
def get_county_name(cty):
    if isinstance(cty, int) and (0 < cty):
        where = "COUN = {}".format(cty)
    elif isinstance(cty, str) and len(cty)==4:
        where = "CTY_ABBR = '{}'".format(cty)
    else:
        raise(ArgumentError)

    with arcpy.da.SearchCursor(COUNTIES, ['CTY_NAME'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise(NotFoundError)


# -----------------------------------------------------------------------------
def get_county_polygon(cty):
    if isinstance(cty, int) and (0 < cty):
        where = "COUN = {}".format(cty)
    elif isinstance(cty, str) and len(cty)==4:
        where = "CTY_ABBR = '{}'".format(cty)
    else:
        raise(ArgumentError)

    with arcpy.da.SearchCursor(COUNTIES, ['SHAPE@'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise(NotFoundError)


# -----------------------------------------------------------------------------
def get_well_data(cty_code):
    if isinstance(cty_code, int) and (0 < cty_code):
        where = ("allwells.COUNTY_C = '{0:2d}' AND allwells.AQUIFER = 'QBAA' "
            "AND C5WL.MEAS_ELEV is not NULL".format(cty_code))
    else:
        raise(ArgumentError)

    joined_table = arcpy.AddJoin_management(WELLS, 'RELATEID', SWLS, 'RELATEID', False)

    ATTRIBUTES = ['allwells.SHAPE', 'C5WL.MEAS_ELEV', 'C5WL.MEAS_DATE', 'allwells.RELATEID']

    welldata = []
    with arcpy.da.SearchCursor(joined_table, ATTRIBUTES, where) as cursor:
        for row in cursor:
            welldata.append(row)

    return welldata
