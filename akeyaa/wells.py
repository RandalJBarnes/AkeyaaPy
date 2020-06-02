"""Define and implement the wells Database class.

Classes
-------
Database
    A load-once-fast-lookup database of authorized wells in Minnesota

Functions
---------
get_welldata_by_polygon(polygon)
    Return well data from across the polygon.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
31 May 2020

"""

import numpy as np
import scipy

import arcpy

from localpaths import SOURCE


# -----------------------------------------------------------------------------
# ArcGIS Pro/ArcPy feature classes of interest.
ALLWELLS = SOURCE['ALLWELLS']
C5WL     = SOURCE['C5WL']

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
class Error(Exception):
    """
    Local base exception.
    """


class ArgumentError(Error):
    """
    The invalid argument.
    """


# -----------------------------------------------------------------------------
class Database:
    """
    A load-once-fast-lookup database of authorized wells in Minnesota.

    Class Attributes
    ----------------
    welldata : list
         The list contains data from authorized wells taken across the state.
         Wells that have multiple static water level measurements in the
         C5WL table will have multiple entries in this table: one entry for
         every measurement.

         There is one or more tuples for each well in the list. The tuples are

            (x, y, z, aquifer)

        where
            x : float
                well x-coordinate in NAD 83 UTM zone 15N [m]

            y : float
                well y-coordinate in NAD 83 UTM zone 15N [m]

            z : float
                measured static water level [ft]

            aquifer : str
                The 4-character aquifer abbreviation string, as defined in
                Minnesota Geologic Survey's coding system.

        For example,
            (232372.0, 5377518.0, 964.0, "QBAA")

    tree : scipy.spatial.cKDTree
        A kd-tree for all of the wells in self.welldata.

    Methods
    -------
    __init__(self)


    __repr__(self)

    __str__(self):

    fetch(self, target, radius)
        Fetch all wells within <radius> of the <target> location.
    """

    # These are class attributes holding a relatively large amount of
    # welldata and the associated spatial kd tree. These class attributes
    # are initialized only once, on the creation of the first Database
    # instance.
    __welldata = None
    __tree = None

    #------------------------
    def __init__(self):
        """On first call, initialize the class attributes.

        Extract the well data from the ArcGIS Pro/ArcPy .gdb, initialize
        the Database.__welldata list, and the Database.__tree spatial
        kd-tree to allow for fast neighborhood searchs. These initializations
        only happen on the first call.
        """

        if Database.__welldata is None:
            table = arcpy.AddJoin_management(ALLWELLS, "RELATEID", C5WL, "RELATEID", False)

            with arcpy.da.SearchCursor(table, ATTRIBUTES, WHERE) as cursor:
                Database.__welldata = [(x, y, z, aq) for (x, y), z, aq in cursor]

            Database.__tree = scipy.spatial.cKDTree([(x, y) for x, y, *_ in Database.__welldata])

    #------------------------
    def __repr__(self):
        return f"{self.__class__}: {len(self.welldata)}"

    #------------------------
    def fetch(self, xtarget, ytarget, radius, aquifers=None):
        """Fetch the (x, y, z) for selected wells.

        Fetch the (x, y, z) data for all authorized wells within <radius>
        of the <target> location that are completed in within one or more
        of the identified <aquifers>.

        Parameters
        ----------
        xtarget : float
            x-coordinate (easting) of the target location in
            NAD 83 UTM zone 15N [m]

        ytarget : float
            y-coordinate (northing) of the target location in
            NAD 83 UTM zone 15N [m]

        radius : float
            The radius of the search neighborhood [m].

        aquifers : list, optional
            List of four-character aquifer abbreviation strings, as defined in
            Minnesota Geologic Survey's coding system. The default is None. If
            None, then wells from all aquifers will be included.

        Returns
        -------
        x : ndarray, shape=(n,), dtype=float
            The well x-coordinates in "NAD 83 UTM zone 15N" (EPSG:26915) [m].

        y : ndarray, shape=(n,), dtype=float
            The well y-coordinates in "NAD 83 UTM zone 15N" (EPSG:26915) [m].

        z : ndarray, shape=(n,), dtype=float
            The measured static water levels [ft].

        Notes
        -----
        o   Beware! The x and coordinates are in [m], but z is in [ft].
        """

        indx = Database.__tree.query_ball_point([xtarget, ytarget], radius)

        if not indx:
            x = []
            y = []
            z = []
        else:
            xyz = []
            for i in indx:
                if (aquifers is None) or (Database.__welldata[i][3] in aquifers):
                    xyz.append(Database.__welldata[i][0:3])
            x, y, z = zip(*xyz)

        return (np.array(x), np.array(y), np.array(z))


# -----------------------------------------------------------------------------
def get_welldata_by_polygon(polygon):
    """Return the welldata from all authorized wells in the polygon

    Extract the welldata from the ArcGIS Pro/ArcPy .gdb using an
    arcpy.SelectLayerByLocation query. This call returns the welldata
    for all authorized wells located in the interior of <polygon> regardless
    of the aquifer in which the wells are completed,.

    Parameters
    ----------
    polygon : arcpy.polygon
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
    table = arcpy.AddJoin_management(ALLWELLS, "RELATEID", C5WL, "RELATEID", False)

    located_wells = arcpy.SelectLayerByLocation_management(
            table,
            select_features=polygon,
            overlap_type="WITHIN",
            selection_type="NEW_SELECTION")

    with arcpy.da.SearchCursor(located_wells, ATTRIBUTES, WHERE) as cursor:
        welldata = [(x, y, z, aq) for (x, y), z, aq in cursor]

    return welldata
