"""
Define and implement the wells Database class.

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
30 May 2020

"""

import numpy as np
import scipy

import arcpy

import localpaths as loc


# -----------------------------------------------------------------------------
# Feature classes of interest.
ALLWELLS = loc.CWIGDB + r'\allwells'                # MN county well index
C5WL     = loc.CWIGDB + r'\C5WL'                    # MN static water levels

# The attributes to be include in "well data".
ATTRIBUTES = ['allwells.SHAPE',
              'C5WL.MEAS_ELEV',
              'allwells.AQUIFER']

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

    Attributes
    ----------
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
            (232372.0, 5377518.0, 964.0, 'QBAA')

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

    def __init__(self):
        """
        Extract the well data from the ArcGIS .gdb and create a kd-tree.
        """

        table = arcpy.AddJoin_management(ALLWELLS, 'RELATEID', C5WL, 'RELATEID', False)

        with arcpy.da.SearchCursor(table, ATTRIBUTES, WHERE) as cursor:
            self.welldata = [(x, y, z, aq) for (x, y), z, aq in cursor]

        self.tree = scipy.spatial.cKDTree([(x, y) for x, y, *_ in self.welldata])

    def __repr__(self):
        return f'{self.__class__}: {len(self.welldata)}'

    def fetch(self, xtarget, ytarget, radius, aquifers=None):
        """
        Fetch authorized wells within <radius> of the <target> location that
        are completed in within one or more of the prescribed <aquifers>.

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
            The well x-coordinates in 'NAD 83 UTM zone 15N' (EPSG:26915) [m].

        y : ndarray, shape=(n,), dtype=float
            The well y-coordinates in 'NAD 83 UTM zone 15N' (EPSG:26915) [m].

        z : ndarray, shape=(n,), dtype=float
            The measured static water levels [ft].

        Notes
        -----
        o   Beware! The x and coordinates are in [m], but z is in [ft].
        """

        indx = self.tree.query_ball_point([xtarget, ytarget], radius)

        xyz = []
        for i in indx:
            if (aquifers is None) or (self.welldata[i][3] in aquifers):
                xyz.append(self.welldata[i][0:3])

        x, y, z = zip(*xyz)
        return (np.array(x), np.array(y), np.array(z))


# -----------------------------------------------------------------------------
def get_welldata_by_polygon(polygon):
    """
    Return the well data from all authorized wells in the polygon

    Parameters
    ----------
    polygon : arcpy.polygon
        The geographic focus of the run.

    Returns
    -------
    welldata : list of tuples (x, y, z, aquifer) where
        x : float
            The well x-coordinates in 'NAD 83 UTM zone 15N' (EPSG:26915) [m].

        y : float
            The well y-coordinates in 'NAD 83 UTM zone 15N' (EPSG:26915) [m].

        z : float
            The measured static water level [ft]

        aquifer : str
            The 4-character aquifer abbreviation string, as defined in
            Minnesota Geologic Survey's coding system.
    """
    table = arcpy.AddJoin_management(ALLWELLS, 'RELATEID', C5WL, 'RELATEID', False)

    located_wells = arcpy.SelectLayerByLocation_management(
            table,
            select_features=polygon,
            overlap_type='WITHIN',
            selection_type='NEW_SELECTION')

    with arcpy.da.SearchCursor(located_wells, ATTRIBUTES, WHERE) as cursor:
        welldata = [(x, y, z, aq) for (x, y), z, aq in cursor]

    return welldata
