"""Define and implement the wells database and associated kd tree.

Extract all of the necessary well data from the .gdb, and create an
associated, index-based, kd-tree for very fast lookup based on coordinates.

"""
import numpy as np
import scipy

import gis


# -----------------------------------------------------------------------------
def fetch(xtarget, ytarget, radius, aquifers=None):
    """Fetch the nearby wells.

    Fetch the (x, y, z) data for all authorized wells within `radius` of the
    target coordinates (`xtarget`, `ytarget`) that are completed in within
    one or more of the identified `aquifers`.

    If there are no wells that satisfy the search criteria, three empty
    ndarrys are returned.

    Parameters
    ----------
    xtarget : float
        x-coordinate (easting) of the target location in
        NAD 83 UTM zone 15N [m].

    ytarget : float
        y-coordinate (northing) of the target location in
        NAD 83 UTM zone 15N [m].

    radius : float
        The radius of the search neighborhood [m].

    aquifers : list[str], optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then wells from all aquifers will be included.

    Returns
    -------
    x : (n,) ndarray
        The well x-coordinates in "NAD 83 UTM zone 15N" (EPSG:26915) [m].

    y : (n,) ndarray
        The well y-coordinates in "NAD 83 UTM zone 15N" (EPSG:26915) [m].

    z : (n,) ndarray
        The measured static water levels [ft].

    Notes
    -----
    * Beware! The x and y coordinates are in [m], but z is in [ft].

    * The first call is slow because it has to extract the data from an
      external .gdb and setup the search tree. Every call after the first
      is very fast.

    """

    # This function uses two function attributes to serve as function static
    # variables -- in the C++ sense. These are:
    #
    #   fetch.welldata
    #   fetch.tree
    #
    # where
    #
    #   welldata : list[tupel] of the form (x, y, z, aquifer) where
    #       x : float
    #           The well x-coordinate in NAD 83 UTM zone 15N [m].
    #
    #       y : float
    #           The well y-coordinate in NAD 83 UTM zone 15N [m].
    #
    #       z : float
    #           The measured static water level [ft].
    #
    #       aquifer : str
    #           The 4-character aquifer abbreviation string, as defined in
    #           Minnesota Geologic Survey's coding system.
    #
    #       For example, (232372.0, 5377518.0, 964.0, "QBAA").
    #
    #    tree : scipy.spatial.cKDTree
    #        A kd-tree for all of the wells in fetch.welldata.
    #
    # The welldata list contains data from all authorized wells taken across
    # the state. Wells that have multiple static water level measurements
    # will have multiple entries in this table -- one entry for every
    # measurement.

    if "welldata" not in fetch.__dict__:
        fetch.welldata = gis.get_all_well_data()
        fetch.tree = scipy.spatial.cKDTree([(row[0], row[1]) for row in fetch.welldata])

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
