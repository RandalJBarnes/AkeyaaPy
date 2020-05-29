"""
Define and implement the Venue class and helper functions.

Classes
-------
class Venue
    A simple container for kind, code, name, and polygon.

Functions
---------
lookup(kind, name)
    Attempt to find the unique venue code from the kind and name.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
28 May 2020

"""

import arcpy
import pyproj

import localpaths as loc


# -----------------------------------------------------------------------------
# Exhaustively enumerate the currently defined venue options.

KIND = {'CITY', 'TOWNSHIP', 'COUNTY', 'WATERSHED', 'SUBREGION', 'STATE'}

SOURCE = {
    'CITY':         loc.CTUGDB + r'\city_township_unorg',
    'TOWNSHIP':     loc.CTUGDB + r'\city_township_unorg',
    'COUNTY':       loc.CTYGDB + r'\mn_county_boundaries',
    'WATERSHED':    loc.WBDGDB + r'\WBDHU10',
    'SUBREGION':    loc.WBDGDB + r'\WBDHU8',
    'STATE':        loc.STAGDB + r'\Boundaries_of_Minnesota'
    }

DATA_ATTRIBUTES = {
    'CITY':         ['NAME', 'SHAPE@'],
    'TOWNSHIP':     ['NAME', 'SHAPE@'],
    'COUNTY':       ['NAME', 'SHAPE@'],
    'WATERSHED':    ['NAME', 'SHAPE@'],
    'SUBREGION':    ['NAME', 'SHAPE@'],
    'STATE':        ['STATE_NAME', 'SHAPE@']
    }

DATA_REQUIREMENTS = {
    'CITY':         "GNIS_ID = '{}' AND CTU_Type = 'CITY'",
    'TOWNSHIP':     "GNIS_ID = '{}' AND CTU_Type = 'TOWNSHIP'",
    'COUNTY':       "CTY_FIPS = {}",
    'WATERSHED':    "HUC10 = '{}'",
    'SUBREGION':    "HUC8 = '{}'",
    'STATE':        "STATE_NAME = 'Minnesota'"
    }

FULLNAME = {
    'CITY':         "City of {}",
    'TOWNSHIP':     "{} Township",
    'COUNTY':       "{} County",
    'WATERSHED':    "{} Watershed",
    'SUBREGION':    "{} Subregion",
    'STATE':        "State of {}",
    }

LOOKUP_ATTRIBUTES = {
    'CITY':         ['GNIS_ID'],
    'TOWNSHIP':     ['GNIS_ID'],
    'COUNTY':       ['CTY_FIPS'],
    'WATERSHED':    ['HUC10'],
    'SUBREGION':    ['HUC8'],
    'STATE':        ['STATE_GNIS_FEATURE_ID']
    }

LOOKUP_REQUIREMENTS = {
    'CITY':         "NAME = '{}' AND CTU_Type = 'CITY'",
    'TOWNSHIP':     "NAME = '{0}' AND CTU_Type = 'TOWNSHIP'",
    'COUNTY':       "CTY_NAME = {}",
    'WATERSHED':    "(NAME = '{}') AND ("
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
        "(STATES = 'MN,WI'))",
    'SUBREGION':    "(NAME = '{}') AND ("
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
        "(STATES = 'MN,WI'))",
    'STATE':    "(STATE_NAME = 'Minnesota')"
    }


# -----------------------------------------------------------------------------
class Error(Exception):
    """
    The base exception for the module.
    """


class UnknownKindError(Error):
    """
    The specified venue kind is not known.
    """


class VenueNotFoundError(Error):
    """
    The requested venue was not found in the database.
    """


# -----------------------------------------------------------------------------
class Venue:
    """
    A simple container for kind, code, name, and polygon.

    Attributes
    ----------
    kind : str
        One of the members of the set:
        {'CITY', 'TOWNSHIP', 'COUNTY', 'WATERSHED', 'SUBREGION', 'STATE'}

    code : str or int
        The identification code form and format depends on the kind.

        -- 'CITY' : str
            The unique 8-digit Geographic Names Information System (GNIS)
            identification number encoded as a string.

            For example, City of Hugo GNIS = '2394440'.

        -- 'TOWNSHIP' : str
            The unique 8-digit Geographic Names Information System (GNIS)
            identification number encoded as a string.

            For example, White Bear Township GNIS = '665981'.

        -- 'COUNTY': int
            The unique 5-digit Federal Information Processing Standards code
            (FIPS), without the initial 2 digits state code.

            For example, Washington County FIPS = 163

        -- 'WATERSHED' : str
            The unique 10-digit hydrologic unit code (HUC10) encoded as a
            string.

            For example, Sunrise River Watershed HUC10 = '0703000504'.

        -- 'SUBREGION' : str
            The unique 8-digit hydrologic unit code (HUC8) encoded as a
            string.

            For example, Twin Cities subregion HUC8 = '07010206'.

        -- 'STATE' : None

    name : str
        The name of the venue as recorded in the associated .gdb file. For
        example "Hugo" or "Rice Creek".

    fullname : str
        The name with the appropriate suffix or prefix. For example, "The
        City of Hugo", the the "Rice Creek Watershed".
    """

    def __init__(self, kind, code=None):
        """

        Parameters
        ----------
        See the class docstring.

        Raises
        ------
        UnknownKindError : This exception is raised when the specified kind
        is not a member of the set KIND.

        VenueNotFoundError: This exception is raised when the venue, as
        specified by the kind and code, could not be found in the database.
        """

        self.kind = kind
        self.code = code

        # Initialize and name and polygon from the AcrGIS Pro gdb file.
        try:
            source = SOURCE[kind]
            where = DATA_REQUIREMENTS[kind].format(code)
            attributes = DATA_ATTRIBUTES[kind]

        except KeyError:
            raise UnknownKindError

        with arcpy.da.SearchCursor(source, attributes, where) as cursor:
            try:
                name, polygon = cursor.next()
            except StopIteration:
                raise VenueNotFoundError

        # Construct the fullname.
        self.name = name
        self.fullname = FULLNAME[kind].format(name)

        # If necessary, convert coordinates from lat/lon to UTM zone 15N.
        if polygon.spatialReference.type == 'Geographic':
            lon = [pnt.X for pnt in polygon.getPart(0)]
            lat = [pnt.Y for pnt in polygon.getPart(0)]
            projector = pyproj.Proj('epsg:26915', preserve_units=False)
            x, y = projector(lon, lat)
            array = arcpy.Array([arcpy.Point(xy[0], xy[1]) for xy in zip(x, y)])
            polygon = arcpy.Geometry('polygon', array, arcpy.SpatialReference(26915))

        self.polygon = polygon

    def __repr__(self):
        return "Venue: '{0.kind}', '{0.code}', '{0.name}', '{0.fullname}'".format(self)

    def __str__(self):
        return "Venue: '{0.kind}', '{0.code}', '{0.name}', '{0.fullname}'".format(self)


# -----------------------------------------------------------------------------
def lookup(kind, name):
    """
    Attempt to find the unique venue code from the kind and name.

    Get the unique township 8-digit Geographic Names Information System (GNIS)
    identification number from the township name. If the township name is NOT
    unique, a list of township codes is returned.

    Parameters
    ----------
    kind : str
        One of the members of the set:
        {'CITY', 'TOWNSHIP', 'COUNTY', 'WATERSHED', 'SUBREGION', 'STATE'}

    name : str
        The venue name. This does NOT include the words like "City of",
        "Township", "County", "Watershed", or "Subregion".

    Returns
    -------
    code : str or int
        The identification code form and format depends on the kind, as given
        below. If a unique code can not be discerned, then a list of codes is
        returned. If no code are found, an empty list is returned.

        -- 'CITY' : str
            The unique 8-digit Geographic Names Information System (GNIS)
            identification number encoded as a string.

            For example, City of Hugo GNIS = '2394440'.

        -- 'TOWNSHIP' : str
            The unique 8-digit Geographic Names Information System (GNIS)
            identification number encoded as a string.

            For example, White Bear Township GNIS = '665981'.

        -- 'COUNTY': int
            The unique 5-digit Federal Information Processing Standards code
            (FIPS), without the initial 2 digits state code.

            For example, Washington County FIPS = 163

        -- 'WATERSHED' : str
            The unique 10-digit hydrologic unit code (HUC10) encoded as a
            string.

            For example, Sunrise River Watershed HUC10 = '0703000504'.

        -- 'SUBREGION' : str
            The unique 8-digit hydrologic unit code (HUC8) encoded as a
            string.

            For example, Twin Cities subregion HUC8 = '07010206'.

        -- 'STATE' : None

    Notes
    -----
    o   Venues outside of the state are ignored.  Nonetheless, redundant
        (non-unique) names do occur for some venues. Such duplicates are rare.
        But, they do exits within the state.

    o   City names are unique in Minnesota. But, the may appear multiple times
        in the database when a city spans multiple counties. Nonetheless,
        the code is unique.

    o   Township names are NOT unique. For example, there are two unique
        townships named "Balsam", one is in Itasca County and the other in
        Aitkin County. This is uncommon, but it does happen.

    o   County names are unique in Minnesota.

    o   Watershed names are NOT unique. For example, there are three unique
        "Rice Creek" watersheds in the US, two of which are in Minnesota:
        one north of the Twin Cites, and one near the northtern border of
        the state.

    o   Subregion names are NOT unique. For example, there are two unique
        "Snake" hydrologic subregions in Minnesota: one north of Thief River
        Falls, and the other east of Brainerd.
    """

    source = SOURCE[kind]
    where = LOOKUP_REQUIREMENTS[kind].format(name)
    attributes = LOOKUP_ATTRIBUTES[kind]

    code = []
    with arcpy.da.SearchCursor(source, attributes, where) as cursor:
        for row in cursor:
            code.append(row[0])

    return code
