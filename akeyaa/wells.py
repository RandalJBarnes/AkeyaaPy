"""
Define and implement the wells Database class.

Classes
-------
Database
    A load-once-fast-lookup database of authorized wells.

Functions
---------
get_welldata_by_polygon(polygon, aquifers=None)
    Return well data from across the polygon.


Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
27 May 2020

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
class Database:
    """
    A load-once-fast-lookup database of authorized wells.

    Attributes
    ----------
    welldata : list of tuples
         The list contains data from authorized wells taken across the state.
         Wells that have multiple static water level measurements in the
         C5WL table will have multiple entries in this table: one entry for
         every measurement.

         There is one or more tuples for each well in the list. The tuples are

            ((x, y), MEAS_ELEV, AQUIFER)

        where
            (x, y) : tuple (float, float)
                well location in NAD 83 UTM zone 15N [m, m]

            MEAS_ELEV : float
                measured static water level [ft]

            AQUIFER : str
                four-character aquifer abbreviation strings, as defined in
                Minnesota Geologic Survey's coding system.

        For example,
            ((395912.43180000037, 5028164.0002999995), 1129.0, 'QWTA')


    tree : scipy.spatial.cKDTree
        A kd-tree for all of the wells in self.welldata.

    Methods
    -------
    __init__(self)


    __repr__(self)

    __str__(self):

    fetch(self, target, radius, aquifers=None)
        Fetch all neighboring wells.
    """

    def __init__(self):
        """
        Get all of the authorized wells from across the state. Create a
        kd-tree using all of the wells.
        """

        table = arcpy.AddJoin_management(ALLWELLS, 'RELATEID', C5WL,
                                         'RELATEID', False)

        self.welldata = []
        with arcpy.da.SearchCursor(table, ATTRIBUTES, WHERE) as cursor:
            for row in cursor:
                self.welldata.append(row)

        self.tree = scipy.spatial.cKDTree([row[0] for row in self.welldata])


    def __repr__(self):
        return 'Wells: {0}'.format(len(self.welldata))

    def __str__(self):
        return 'Wells: {0}'.format(len(self.welldata))


    def fetch(self, target, radius, aquifers=None):
        """
        Fetch all neighboring wells.

        Fetch all wells that are within radius of the target and are
        completed in one of the aquifers.

        Parameters
        ----------
        target : tuple (x, y) (float, float)
            The (x, y) location of the target point.

        radius : float
            The radius of the search neighborhood.

        aquifers: list of str
            List of four-character aquifer abbreviation strings, as defined in
            Minnesota Geologic Survey's coding system. The default is None. If
            None, then all aquifers present will be included.

        Returns
        -------
            x : ndarray, shape=(n, ), dtype=float
                array of x-coordinates [m].

            y : ndarray, shape=(n, ), dtype=float
                array of y-coordinates [m].

            z : ndarray, shape=(n, ), dtype=float
                array of measured static water levels [ft].

        Notes
        -----
        o   Coordinates are in 'NAD 83 UTM 15N'(EPSG:26915).

        o   Beware! (x, y) are in [m], but z is in [ft].
        """

        indx = self.tree.query_ball_point(target, radius)

        x = []
        y = []
        z = []

        for i in indx:
            wd = self.welldata[i]
            if (aquifers is None) or (wd[2] in aquifers):
                x.append(wd[0][0])
                y.append(wd[0][1])
                z.append(wd[1]])

        return (np.array(x), np.array(y), np.array(z))


# -----------------------------------------------------------------------------
def get_welldata_by_polygon(polygon, aquifers=None):
    """
    Return well data from across the polygon.

    Return the well data from all authorized wells in the polygon that are
    completed in one of the identified aquifers.

    Parameters
    ----------
    polygon : arcpy.polygon
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

    table = arcpy.AddJoin_management(ALLWELLS, 'RELATEID', C5WL, 'RELATEID',
                                     False)

    located_wells = arcpy.SelectLayerByLocation_management(
        table,
        select_features=polygon,
        overlap_type='WITHIN',
        selection_type='NEW_SELECTION')

    welldata = []
    with arcpy.da.SearchCursor(located_wells, ATTRIBUTES, WHERE) as cursor:
        for row in cursor:
            welldata.append(row)

    return welldata
