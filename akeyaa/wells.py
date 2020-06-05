"""Define and implement the wells Database class.

Classes
-------
Database
    A load-once-fast-lookup database of authorized wells in Minnesota

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
04 June 2020

"""

import numpy as np
import scipy

import gis


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

        Extract the well data from the .gdb. On first call, initialize the
        -- Database.__welldata list, and the
        -- Database.__tree spatial kd-tree
        to allow for fast neighborhood searchs.
        """

        if Database.__welldata is None:
            Database.__welldata = gis.get_all_well_data()
            Database.__tree = scipy.spatial.cKDTree([(x, y) for x, y, *_ in Database.__welldata])

    #------------------------
    def __repr__(self):
        return f"{self.__class__}: {len(self.__welldata)}"

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
