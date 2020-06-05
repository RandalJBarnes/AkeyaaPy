"""Define and implement the wells database and associated kd tree.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
05 June 2020

"""

import numpy as np
import scipy

import gis


# -----------------------------------------------------------------------------
def fetch(xtarget, ytarget, radius, aquifers=None):
    """Fetch the nearby wells.

    Fetch the (x, y, z) data for all authorized wells within <radius> of the
    target coordinates that are completed in within one or more of the
    identified <aquifers>.

    If there are no wells that satisfy the search conditions, then empty
    ndarrys are returned.

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

    Function Attributes
    -------------------
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

    Notes
    -----
    o   Beware! The x and coordinates are in [m], but z is in [ft].

    o   This function uses function attributes to serve as function static
        variables, in the C++ sense. The first call is slow because it
        has to extract the data from a .gdb and setup the kd tree.

    o   Every call after the first is very fast.
    """

    if 'welldata' not in fetch.__dict__:
        fetch.welldata = gis.get_all_well_data()
        fetch.tree = scipy.spatial.cKDTree([(x, y) for x, y, *_ in fetch.welldata])

    indx = fetch.tree.query_ball_point([xtarget, ytarget], radius)

    if indx:
        xyz = []
        for i in indx:
            if (aquifers is None) or (fetch.welldata[i][3] in aquifers):
                xyz.append(fetch.welldata[i][0:3])
        x, y, z = zip(*xyz)
    else:
        x = y = z = []

    return (np.array(x), np.array(y), np.array(z))
