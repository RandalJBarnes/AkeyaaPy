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
02 June 2020

"""

import arcpy

from localpaths import SOURCE


# -----------------------------------------------------------------------------
def lookup(name, kind):
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


