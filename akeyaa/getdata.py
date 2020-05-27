"""
A set of functions to retrieve data from specific ArgGIS Pro .gdb files.

Functions
---------

----- get well data -----
get_well_data(aquifers)
    Return well data from across Minnesota.

get_well_data_by_polygon(polygon, aquifers)
    Return well data from across the polygon.

----- state -----
get_state_polygon()
    Get the Minnesota state boundary polygon.

----- county -----
get_county_code(cty_abbr)
    Get the county code from the county abbreviation.

get_county_abbr(cty_code)
    Get the county abbreviation from the county code.

get_county_name(cty_abbr)
    Get the county name from the county abbreviation.

get_county_polygon(cty_abbr)
    Get the county polygon from the county abbreviation.

----- township and section -----
get_township_polygon(twnshp, rng)
    Get the township polygon.

get_section_polygon(twnshp, rng, sctn)
    Get the section polygon.

----- hydrologic watershed -----
get_watershed_name(wtrs_code)
    Get the watershed name from the watershed code (HUC10).

get_watershed_code(wtrs_name)
    Get the watershed code (HUC10) from the watershed name.

get_watershed_polygon(wtrs_code)
    Get the watershed polygon from the watershed code (HUC10).

----- hydrologic subregion -----
get_subregion_name(subr_code)
    Get the subregion name from the watershed code (HUC8).

get_subregion_code(subr_name)
    Get the subregion code (HUC8) from the watershed name.

get_subregion_polygon(subr_code)
    Get the subregion polygon from the watershed code (HUC8).

Notes
-----
o   Make sure that the localization file is present, correct, and complete.
o   Our working coordinates are in 'NAD 83 UTM 15N'(EPSG:26915).

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
27 May 2020

"""

import pyproj
import arcpy

import localization as loc


# Feature classes of interest.
MNBDRY   = loc.STALOC + r'\Boundaries_of_Minnesota' # MN state boundary
TWNBDRY  = loc.TRSLOC + r'\tr'                      # MN townships
SECBDRY  = loc.TRSLOC + r'\trs'                     # MN sections
CTYBDRY  = loc.CTYLOC + r'\mn_county_boundaries'    # MN counties
ALLWELLS = loc.CWILOC + r'\allwells'                # MN county well index
C5WL     = loc.CWILOC + r'\C5WL'                    # MN static water levels
WBDHU10  = loc.WBDLOC + r'\WBDHU10'                 # US hydrologic watersheds
WBDHU8   = loc.WBDLOC + r'\WBDHU8'                  # US hydrologic subregions

# The attributes to be include in "well data".
ATTRIBUTES = ['allwells.SHAPE',
              'C5WL.MEAS_ELEV',
              'C5WL.MEAS_DATE',
              'allwells.AQUIFER',
              'allwells.RELATEID']

# Wells that satisfy all of these criteria are called "authorized wells".
# These include: must have at least one recorded static water level (SWL),
# must have an identified aquifer, and must be located.
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
def get_well_data(aquifers=None):
    """
    Return well data from across Minnesota.

    Return the well data from all authorized wells in Minnesota that are
    completed in one of the identified aquifers.

    Parameters
    ----------
    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

    Returns
    -------
    welldata : list
        Each element in the list is a tuple containing all of the attributes
        included in the ATTRIBUTES constant (see above).

    Notes
    -----
    o   Coordinates are in 'NAD 83 UTM 15N'(EPSG:26915).
    o   This is a relatively slow (i.e. > 5 seconds) function call.
    """

    where = WHERE

    if aquifers is not None:
        if isinstance(aquifers, list):
            where += " AND ("

            for i, code in enumerate(aquifers):
                if i != 0:
                    where += " OR "
                where += "(allwells.AQUIFER = '{}')".format(code)
            where += ")"
        else:
            raise ArgumentError

    joined_table = arcpy.AddJoin_management(
            ALLWELLS, 'RELATEID', C5WL, 'RELATEID', False)

    welldata = []
    with arcpy.da.SearchCursor(joined_table, ATTRIBUTES, where) as cursor:
        for row in cursor:
            welldata.append(row)

    return welldata


# -----------------------------------------------------------------------------
def get_well_data_by_polygon(polygon, aquifers=None):
    """
    Return well data from across the polygon.

    Return the well data from all authorized wells in the polygon that are
    completed in one of the identified aquifers.

    Parameters
    ----------
    polygon : arcpy.polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the run.

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

    Returns
    -------
    welldata : list
        Each element in the list is a tuple containing all of the attributes
        included in the ATTRIBUTES constant (see above).

    Notes
    -----
    o   Coordinates are in 'NAD 83 UTM 15N'(EPSG:26915).
    """

    where = WHERE

    if aquifers is not None:
        if isinstance(aquifers, list):
            where += " AND ("

            for i, code in enumerate(aquifers):
                if i != 0:
                    where += " OR "
                where += "(allwells.AQUIFER = '{}')".format(code)
            where += ")"
        else:
            raise ArgumentError

    joined_table = arcpy.AddJoin_management(
            ALLWELLS, 'RELATEID', C5WL, 'RELATEID', False)

    located_wells = arcpy.SelectLayerByLocation_management(
        joined_table,
        select_features=polygon,
        overlap_type='WITHIN',
        selection_type='NEW_SELECTION')

    welldata = []
    with arcpy.da.SearchCursor(located_wells, ATTRIBUTES, where) as cursor:
        for row in cursor:
            welldata.append(row)

    return welldata


# -----------------------------------------------------------------------------
def get_state_polygon():
    """
    Get the Minnesota state boundary polygon.

    Parameters
    ----------
    None

    Returns
    -------
    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the query.

    Notes
    -----
    o   Coordinates are in 'NAD 83 UTM 15N'(EPSG:26915).
    """

    with arcpy.da.SearchCursor(MNBDRY, ['SHAPE@']) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_code(cty_abbr):
    """
    Get the county code number from the county abbreviation.

    Return the 2-digit county identification number as defined by the
    Minnesota County Well Index project of the Minnesota Geologic Survey.

        http://mgsweb2.mngs.umn.edu/cwi_doc/county.asp?=

    These first 87 of these county code numbers align with an alphabetial
    listing of the Minnesota county names. These county code numbers are NOT
    the county FIPS numbers.

    These codes includes numbers for wells that are present in the Minnesota
    County Well Index but located in Iowa (88), Wisconsin (89), North
    Dakota (90), South Dakota (91), and Canada (92). There is also a code
    for "Unknown" (99).

    These county code numbers are the same as the COUNTY_C field of the
    "allwells" geodatabase feature class. However, the COUNTY_C values are
    encoded as characrter strings.

    Parameters
    ----------
    cty_abbr : str
        The 4-character county abbreviation string, as defined by the
        Minnesota Department of Natural Resources.

    Returns
    -------
    cty_code : int
        The 2-digit county identification number as defined by the Minnesota
        County Well Index project of the Minnesota Geologic Survey. These are
        not the FIPS codes.
    """

    where = "CTY_ABBR = '{0}'".format(cty_abbr)

    with arcpy.da.SearchCursor(CTYBDRY, ['COUN'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_abbr(cty_code):
    """
    Get the county abbreviation from the county code.

    Parameters
    ----------
    cty_code : int
        The 2-digit county identification number as defined by the Minnesota
        County Well Index project of the Minnesota Geologic Survey. These are
        not the FIPS codes.

    Returns
    -------
    cty_abbr : str
        The 4-character county abbreviation string, as defined by the
        Minnesota Department of Natural Resources.

    Notes
    -----
    o   See get_county_code for details on the meaning and origin of the
        county codes.
    """

    where = "COUN = {}".format(cty_code)

    with arcpy.da.SearchCursor(CTYBDRY, ['CTY_ABBR'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_name(cty_abbr):
    """
    Get the county name from the county abbreviation.

    Parameters
    ----------
    cty_abbr : str
        The 4-character county abbreviation string, as defined by the
        Minnesota Department of Natural Resources.

    Returns
    -------
    name : str
        The complete official name of the county.
    """

    where = "CTY_ABBR = '{}'".format(cty_abbr)

    with arcpy.da.SearchCursor(CTYBDRY, ['CTY_NAME'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_county_polygon(cty_abbr):
    """
    Get the county polygon from the county abbreviation.

    Parameters
    ----------
    cty_abbr : str
        The 4-character county abbreviation string, as defined by the
        Minnesota Department of Natural Resources.

    Returns
    -------
    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the query.
    """

    where = "CTY_ABBR = '{}'".format(cty_abbr)

    with arcpy.da.SearchCursor(CTYBDRY, ['SHAPE@'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_township_polygon(twnshp, rng):
    """
    Get the township polygon.

    Parameters
    ----------
    twnshp : int
        Township number.

    rng : int
        Range number.

    Returns
    -------
    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the query.

    Notes
    -----
    o   Coordinates are in 'NAD 83 UTM 15N'(EPSG:26915).
    """

    where = "TOWN = {0:d} AND RANG = {1:d}".format(twnshp, rng)

    with arcpy.da.SearchCursor(TWNBDRY, ['SHAPE@'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_section_polygon(twnshp, rng, sctn):
    """
    Get the section polygon.

    Parameters
    ----------
    twnshp : int
        Township number.

    rng : int
        Range number.

    sctn : int
        Section number.

    Returns
    -------
    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the query.

    Notes
    -----
    o   Coordinates are in 'NAD 83 UTM 15N'(EPSG:26915).
    """

    where = ("TOWN = {0:d} AND RANG = {1:d} AND SECT = {2:d}"
             .format(twnshp, rng, sctn))

    with arcpy.da.SearchCursor(SECBDRY, ['SHAPE@'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_watershed_code(wtrs_name):
    """
    Get the watershed code (HUC10) from the watershed name.

    Parameters
    ----------
    wtrs_name : str
        The watershed name string as defined in the U.S. Geological Survey
        Watershed Boundary Dataset. These are not unique.

    Returns
    -------
    codes : list of tuples
        (code, state)
        wtrs_code : str
            10-digit watershed number encoded as a string (HUC10).
        state : str
            Two character state abbreviations; e.g. 'MN'.

    Notes
    -----
    o   Watershed names are NOT unique. For example, there are three unique
        "Rice Creek" watersheds, two of which are in Minnesota: one north of
        the Twin Cites, and one near the northtern border of the state.

    References
    ----------
    https://www.usgs.gov/core-science-systems/ngp/national-hydrography/
        access-national-hydrography-products
    """

    where = "(NAME = '{0}')".format(wtrs_name)

    codes = []
    with arcpy.da.SearchCursor(WBDHU10, ['HUC10', 'STATES'], where) as cursor:
        try:
            for row in cursor:
                codes.append(row)
        except StopIteration:
            raise NotFoundError

    return codes


# -----------------------------------------------------------------------------
def get_watershed_name(wtrs_code):
    """
    Get the watershed name from the watershed code (HUC10).

    Parameters
    ----------
    wtrs_code : str
        The 10-digit watershed number encoded as a string (HUC10).

    Returns
    -------
    WBDHU10 : str
        The watershed name string as defined in the U.S. Geological Survey
        Watershed Boundary Dataset. These are not unique.
    """

    where = "HUC10 = '{0}'".format(wtrs_code)

    with arcpy.da.SearchCursor(WBDHU10, ['NAME'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_watershed_polygon(wtrs_code):
    """
    Get the watershed polygon from the watershed code (HUC10).

    Parameters
    ----------
    wtrs_code : str
        The 10-digit watershed number encoded as a string (HUC10).

    Returns
    -------
    poly26915 : arcpy.polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the query.

        The returned polygon uses EPSG:26915 coordinates -- i.e. NAD 83
        UTM zone 15N.

    Notes
    -----
    o   This function gets the polygon from WBD_National_GDB.gdb, then
        creates a new polygon with the original EPSG:7019 coordinates
        converted to EPSG:26915 coordinates.
    """

    where = "HUC10 = '{0}'".format(wtrs_code)

    with arcpy.da.SearchCursor(WBDHU10, ['SHAPE@'], where) as cursor:
        try:
            poly7019 = cursor.next()[0]
        except StopIteration:
            raise NotFoundError

    poly26915 = convert_polygon(poly7019)
    return poly26915


# -----------------------------------------------------------------------------
def get_subregion_code(subr_name):
    """
    Get the subregion code(s) (HUC8) from the watershed name.

    Parameters
    ----------
    subr_name : str
        The hydrologic subregion name string as defined in the U.S. Geological
        Survey Watershed Boundary Dataset. These are not unique.

    Returns
    -------
    codes : list of tuples
        (code, state)
        subr_code : str
            The 8-digit subregion number encoded as a string (HUC8).
        state : str
            Two character state abbreviations; e.g. 'MN'.

    Notes
    -----
    o   Subregion names are NOT unique. For example, there are two unique
        "Snake" hydrologic subregions in Minnesota: one north of Thief River
        Falls, and the other east of Brainerd.

    References
    ----------
    https://www.usgs.gov/core-science-systems/ngp/national-hydrography/
        access-national-hydrography-products
    """

    where = "NAME = '{0}'".format(subr_name)

    codes = []
    with arcpy.da.SearchCursor(WBDHU8, ['HUC8', 'STATES'], where) as cursor:
        try:
            for row in cursor:
                codes.append(row)
        except StopIteration:
            raise NotFoundError

    return codes


# -----------------------------------------------------------------------------
def get_subregion_name(subr_code):
    """
    Get the subregion name from the subregion code (HUC8).

    Parameters
    ----------
    subr_code : str
        The 8-digit subregion number encoded as a string (HUC8).

    Returns
    -------
    subr_name : str
        The hydrologic subregion name string as defined in the U.S. Geological
        Survey Watershed Boundary Dataset. These are not unique.
    """

    where = "HUC8 = '{0}'".format(subr_code)

    with arcpy.da.SearchCursor(WBDHU8, ['NAME'], where) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError


# -----------------------------------------------------------------------------
def get_subregion_polygon(subr_code):
    """
    Get the subregion polygon from the subregion code (HUC8).

    Parameters
    ----------
    subr_code : str
        The 8-digit subregion number encoded as a string (HUC8).

    Returns
    -------
    poly26915 : arcpy.polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the query.

        The returned polygon uses EPSG:26915 coordinates -- i.e. NAD 83
        UTM zone 15N.

    Notes
    -----
    o   This function gets the polygon from WBD_National_GDB.gdb, then
        creates a new polygon with the original EPSG:7019 coordinates
        converted to EPSG:26915 coordinates.
    """

    where = "HUC8 = '{0}'".format(subr_code)

    with arcpy.da.SearchCursor(WBDHU8, ['SHAPE@'], where) as cursor:
        try:
            poly7019 = cursor.next()[0]
        except StopIteration:
            raise NotFoundError

    poly26915 = convert_polygon(poly7019)
    return poly26915


# -----------------------------------------------------------------------------
def convert_polygon(poly7019):
    """
    Parameters
    ----------
    poly7019 : arcpy.polygon
        This polygon uses EPSG:7019 coordinates -- i.e. lat/lon.

    Returns
    -------
    poly26915 : arcpy.polygon
        This polygon uses EPSG:26915 coordinates -- i.e. NAD 83 UTM 15N

    Notes
    -----
    o   The WBD_National_GDB.gdb polygons are stored using lat/lon coordinates;
        more specifically 'GRS 1980' (EPSG:7019), which is a precursor of
        'WGS 84' (EPSG:4326).

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

    # Extract the polygon vertices in EPSG:7019.
    lon7019 = [pnt.X for pnt in poly7019.getPart(0)]
    lat7019 = [pnt.Y for pnt in poly7019.getPart(0)]

    # Convert from EPSG:7019 to EPSG:26915
    crs_utm = pyproj.CRS.from_user_input(26915)
    crs_latlon = pyproj.CRS.from_user_input(4326)
    transformer = pyproj.Transformer.from_crs(crs_latlon, crs_utm)
    x26915, y26915 = transformer.transform(lat7019, lon7019)

    # Create the new arcpy.polygon.
    xy26915 = list(zip(x26915, y26915))
    array26915 = arcpy.Array([arcpy.Point(pt[0], pt[1]) for pt in xy26915])
    poly26915 = arcpy.Geometry(
            'polygon', array26915, arcpy.SpatialReference(26915))

    return poly26915
