"""Define and implement the Venue class and all of its subclasses, along with
a few helper functions.

Classes
-------
class Venue
    Abstract base class for all Venue.

class City
    City subclass of Venue.

class Township
    Township subclass of Venue.

class County
    County subclass of Venue.

class Watershed
    Watershed subclass of Venue.

class Subregion
    Subregion subclass of Venue.

Functions
---------
convert_polygon(polygon)
    Convert a polygon's coordinates from lat/lon to UTM.

lookup_code(kind, name)
    Attempt to find the unique venue code from the name and kind.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
31 May 2020

"""

import arcpy
import pyproj

import localpaths as loc


# -----------------------------------------------------------------------------
KIND = {"CITY", "TOWNSHIP", "COUNTY", "WATERSHED", "SUBREGION", "STATE"}

SOURCE = {
    "CITY":      loc.CTUGDB + r"\city_township_unorg",
    "TOWNSHIP":  loc.CTUGDB + r"\city_township_unorg",
    "COUNTY":    loc.CTYGDB + r"\mn_county_boundaries",
    "WATERSHED": loc.WBDGDB + r"\WBDHU10",
    "SUBREGION": loc.WBDGDB + r"\WBDHU8",
    "STATE":     loc.STAGDB + r"\Boundaries_of_Minnesota"
    }


# -----------------------------------------------------------------------------
class Error(Exception):
    """The base exception for the module. """


class VenueNotFoundError(Error):
    """The requested venue was not found in the database. """


class UnknownKindError(Error):
    """The specified kind is not supported."""


# -----------------------------------------------------------------------------
class Venue:
    """The (abstract) base class for all Venues.

    The subclass Venues include "CITY", "TOWNSHIP", "COUNTY", "WATERSHED",
    "SUBREGION", and "STATE".

    Attributes
    ----------
    code : str or int
        The unique identification code for the venue.

        The form and format depends on the kind of venue, as defined by
        the subclass.

        -- "CITY" : str
            The unique 8-digit Geographic Names Information System (GNIS)
            identification number encoded as a string.

            For example, City of Hugo GNIS = "2394440".

        -- "TOWNSHIP" : str
            The unique 8-digit Geographic Names Information System (GNIS)
            identification number encoded as a string.

            For example, White Bear Township GNIS = "665981".

        -- "COUNTY": int
            The unique 5-digit Federal Information Processing Standards code
            (FIPS), without the initial 2 digits state code.

            For example, Washington County FIPS = 163

        -- "WATERSHED" : str
            The unique 10-digit hydrologic unit code (HUC10) encoded as a
            string.

            For example, Sunrise River Watershed HUC10 = "0703000504".

        -- "SUBREGION" : str
            The unique 8-digit hydrologic unit code (HUC8) encoded as a
            string.

            For example, Twin Cities subregion HUC8 = "07010206".

        -- "STATE" : None

    name : str
        The name of the venue as recorded in the associated .gdb file. For
        example "Hugo" or "Rice Creek".

    fullname : str
        The name with the appropriate suffix or prefix. For example, "The
        City of Hugo", the the "Rice Creek Watershed".

    polygon : arcpy.arcobjects.geometries.Polygon
        An arcpy.Polygon with the vertex coordinates represented in
        "NAD 83 UTM zone 15N" (EPSG:26915),

    Subclass Constants
    -------------------
    WHO : str
        The format string for converting a name into a full name.

    WHAT : str
        The feature class attribute names used to extract the name and polygon
        from the feature class.

    WHEN : str
        The format string for generating the arcpy query requirements.

    WHERE : str
        The full path to the .gdb and feature class.
    """

    # -----------------------
    def __init__(self, code):
        """The initializer for all Venue subclasses.

        The subclasses do not have their own __init__. To eliminate code
        duplication, the initialization is all done here in the base class
        __init__. The subclass specialization is done via the small set of
        subclass constants.

        Parameters
        ----------
        code : str, or list of str
            See the class docstring for more details.

            This initializer allows chaining the output from venues.lookup
            as input directly into the Venue subclass constructor: e.g.

                my_venue = City(lookup("CITY", "Hugo"))

            To allow this, if a list of code strings is pass in then the
            first code string in the list is used.

        Raises
        ------
        VenueNotFoundError: This exception is raised when the venue, as
        specified by the kind and code, could not be found in the database.

        """

        if isinstance(code, list):
            code = code[0]

        with arcpy.da.SearchCursor(
                self.WHERE,
                self.WHAT,
                self.WHEN.format(code)
                ) as cursor:
            try:
                name, polygon = cursor.next()
            except StopIteration:
                raise VenueNotFoundError

        self.code = code
        self.name = name
        self.fullname = self.WHO.format(name)

        if polygon.spatialReference.type == "Geographic":
            self.polygon = convert_polygon(polygon)
        else:
            self.polygon = polygon

    # -----------------------
    def __repr__(self):
        return f"{self.__class__}: {self.code}, {self.name}"

    # -----------------------
    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)


# -----------------------------------------------------------------------------
class City(Venue):
    """City subclass of Venue."""

    WHO = "City of {}"
    WHAT = ["NAME", "SHAPE@"]
    WHEN = "GNIS_ID = '{}' AND CTU_Type = 'CITY'"
    WHERE = SOURCE["CITY"]


# -----------------------------------------------------------------------------
class Township(Venue):
    """Township subclass of Venue."""

    WHO = "{} Township"
    WHAT = ["NAME", "SHAPE@"]
    WHEN = "GNIS_ID = '{}' AND CTU_Type = 'TOWNSHIP'"
    WHERE = SOURCE["TOWNSHIP"]


# -----------------------------------------------------------------------------
class County(Venue):
    """County subclass of Venue."""

    WHO = "{} County"
    WHAT = ["CTY_NAME", "SHAPE@"]
    WHEN = "CTY_FIPS = {}"
    WHERE = SOURCE["COUNTY"]


# -----------------------------------------------------------------------------
class Watershed(Venue):
    """Watershed subclass of Venue."""

    WHO = "{} Watershed"
    WHAT = ["NAME", "SHAPE@"]
    WHEN = "HUC10 = '{}'"
    WHERE = SOURCE["WATERSHED"]


# -----------------------------------------------------------------------------
class Subregion(Venue):
    """Subregion subclass of Venue."""
    WHO = "{} Subregion"
    WHAT = ["NAME", "SHAPE@"]
    WHEN = "HUC8 = '{}'"
    WHERE = SOURCE["SUBREGION"]


# -----------------------------------------------------------------------------
class State(Venue):
    """State subclass of Venue."""

    WHO = "State of {}"
    WHAT = ["STATE_NAME", "SHAPE@"]
    WHEN = "STATE_NAME = 'Minnesota'"
    WHERE = SOURCE["STATE"]


# -----------------------------------------------------------------------------
def convert_polygon(polygon):
    """Convert a polygon's coordinates from lat/lon to UTM.

    Takes in an arcpy.Polygon that uses "GCS North America 1983" (EPSG:4269)
    lat/lon coordinates. Creates and returns a new arcpy.Polygon that has
    the same vertices re-expressed in "NAD 83 UTM zone 15N" (EPSG:26915)
    coordinates.

    This conversion is actually from "WGS 1984" not "GCS 1983", but these two
    are close enough for our purposes.

    Arguments
    ---------
    polygon : arcpy.arcobjects.geometries.Polygon
        An arcpy.Polygon in lat/lon.

    Returns
    -------
    polygon : arcpy.arcobjects.geometries.Polygon
        An arcpy.Polygon in UTM 15N.
    """

    lon = [pnt.X for pnt in polygon.getPart(0)]
    lat = [pnt.Y for pnt in polygon.getPart(0)]

    sr_out = arcpy.SpatialReference(26915)
    projector = pyproj.Proj("epsg:26915", preserve_units=False)

    x, y = projector(lon, lat)
    array = arcpy.Array([arcpy.Point(xy[0], xy[1]) for xy in zip(x, y)])

    return arcpy.Geometry("polygon", array, sr_out)


# -----------------------------------------------------------------------------
def lookup_code(name, kind):
    """Attempt to find the unique venue code from the kind and name.

    Get the unique township 8-digit Geographic Names Information System (GNIS)
    identification number from the township name. If the township name is NOT
    unique, a list of township codes is returned.

    Parameters
    ----------
    name : str
        The case-sensitive venue name. This name must match exactly to the
        name in the associated .gdf feature class.

        Note: this name does NOT include the words like "City of", "Township",
        "County", "Watershed", or "Subregion".

    kind : str
        The case-insensitve kind of Venue: one of the members of the set:
        {"CITY", "TOWNSHIP", "COUNTY", "WATERSHED", "SUBREGION", "STATE"}

    Returns
    -------
    code : str or int
        The identification code form and format depends on the kind, as given
        below. If a unique code can not be discerned, then a list of codes is
        returned. If no code are found, an empty list is returned.

        -- "CITY" : str
            The unique 8-digit Geographic Names Information System (GNIS)
            identification number encoded as a string.

            For example, City of Hugo GNIS = "2394440".

        -- "TOWNSHIP" : str
            The unique 8-digit Geographic Names Information System (GNIS)
            identification number encoded as a string.

            For example, White Bear Township GNIS = "665981".

        -- "COUNTY": int
            The unique 5-digit Federal Information Processing Standards code
            (FIPS), without the initial 2 digits state code.

            For example, Washington County FIPS = 163

        -- "WATERSHED" : str
            The unique 10-digit hydrologic unit code (HUC10) encoded as a
            string.

            For example, Sunrise River Watershed HUC10 = "0703000504".

        -- "SUBREGION" : str
            The unique 8-digit hydrologic unit code (HUC8) encoded as a
            string.

            For example, Twin Cities subregion HUC8 = "07010206".

        -- "STATE" : None

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

    LOOKUP_ATTRIBUTES = {
        "CITY":         ["GNIS_ID"],
        "TOWNSHIP":     ["GNIS_ID"],
        "COUNTY":       ["CTY_FIPS"],
        "WATERSHED":    ["HUC10"],
        "SUBREGION":    ["HUC8"],
        "STATE":        ["STATE_GNIS_FEATURE_ID"]
        }

    LOOKUP_REQUIREMENTS = {
        "CITY":         "NAME = '{}' AND CTU_Type = 'CITY'",
        "TOWNSHIP":     "NAME = '{}' AND CTU_Type = 'TOWNSHIP'",
        "COUNTY":       "CTY_NAME = '{}'",
        "WATERSHED":    "(NAME = '{}') AND ("
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
        "SUBREGION":    "(NAME = '{}') AND ("
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
        "STATE":    "(STATE_NAME = 'Minnesota')"
        }

    try:
        kind = kind.upper()
        source = SOURCE[kind]
        attributes = LOOKUP_ATTRIBUTES[kind]
        where = LOOKUP_REQUIREMENTS[kind].format(name)
    except KeyError:
        raise UnknownKindError(f'{kind} is not a recognized kind.')

    code = []
    with arcpy.da.SearchCursor(source, attributes, where) as cursor:
        for row in cursor:
            code.append(row[0])

    return code
