"""Define and implement the wells database and associated kd tree.

Extract all of the necessary well data from the .gdb, and create an
associated, index-based, kd-tree for very fast lookup based on coordinates.

"""
from bisect import bisect_left
from operator import itemgetter
import scipy

from akeyaa.gis import get_all_well_data


class Wells(object):
    """Create and manage the in-memory, python-based, well database.

    Attributes
    ----------
    __welldata : list[tuple] ((x, y), z, aquifer, relateid)
        (x, y) : tuple(float, float)
            The x- and y-coordinates in "NAD 83 UTM 15N" (EPSG:26915) [m].

        z : float
            The recorded static water level [ft]

        aquifer : str
            The 4-character aquifer abbreviation string, as defined in
            Minnesota Geologic Survey's coding system.

        relateid : str
            The unique 10-digit well number encoded as a string with
            leading zeros.

        For example: ((232372.0, 5377518.0), 964.0, 'QBAA', '0000153720')
        The welldata is sorted by the relateid.

    __relateid : list[str]
        The unique 10-digit well number encoded as a string with
        leading zeros.

    __tree : scipy.spatial.cKDTree
        A kd-tree for all of the wells in fetch.welldata.

    Notes
    -----
    *   The welldata list contains data from all authorized wells taken across
        the state. Wells that have multiple static water level measurements
        will have multiple entries in this table -- one entry for every
        measurement.

    *   The __relateid list is created as a search key.

    """
    __welldata = None
    __relateid = None
    __tree = None


    @classmethod
    def __initialize(cls):
        if cls.__welldata is None:
            cls.__welldata = sorted(get_all_well_data(), key=itemgetter(3))
            cls.__relateid = [row[3] for row in cls.__welldata]
            cls.__tree = scipy.spatial.cKDTree([row[0] for row in cls.__welldata])

    def __init__(self):
        """Setup the data and kd-tree in memory.

        Notes
        -----
        The first call is slow because it has to extract the data from an
        external .gdb, thensetup the kd search tree and the sorted id list.
        Every call after the first is very fast.

        """
        if Wells.__welldata is None:
            Wells.__initialize()

    def fetch(self, xytarget, radius, aquifers=None):
        """Fetch the nearby wells.

        Fetch the welldata for all authorized wells within `radius` of the
        coordinates `xytarget` that are completed in one or more of the
        identified `aquifers`.

        Parameters
        ----------
        xytarget : tuple(float, float)
            x-coordinate (easting) and y-coordinate (northing) of the target
            location in NAD 83 UTM zone 15N [m].

        radius : float
            The radius of the search neighborhood [m].

        aquifers : list[str], optional
            List of four-character aquifer abbreviation strings, as defined in
            Minnesota Geologic Survey's coding system. The default is None. If
            None, then wells from all aquifers will be included.

        Returns
        -------
        list[tuple] : ((x, y), z, aquifer, relateid)
            Returns a list of tuples, with one tuple for each welldata entry
            that satisfies the search criteria. If there are no wells that
            satisfy the search criteria an empty list is returned.

        Notes
        -----
        * Beware! The x and y coordinates are in [m], but z is in [ft].

        """
        welldata = []
        indx = Wells.__tree.query_ball_point(xytarget, radius)
        if indx:
            for i in indx:
                if (aquifers is None) or (Wells.__welldata[i][2] in aquifers):
                    welldata.append(Wells.__welldata[i])
        return welldata

    def fetch_by_venue(self, venue, aquifers=None):
        """Fetch wells in the specified venue.

        Fetch the ((x, y), z) data for all authorized wells within `venue`
        that are completed in one or more of the identified `aquifers`.

        Parameters
        ----------
        venue: type
            An instance of a political division, administrative region, or
            user-defined domain, as enumerated and detailed in `akeyaa.venues`.
            For example: a ``City``, ``Watershed``, or ``Neighborhood``.

        aquifers : list[str], optional
            List of four-character aquifer abbreviation strings, as defined in
            Minnesota Geologic Survey's coding system. The default is None. If
            None, then wells from all aquifers will be included.

        Returns
        -------
        list[tuple] : ((x, y), z, aquifer, relateid)
            Returns a list of tuples, with one tuple for each welldata entry
            that satisfies the search criteria. If there are no wells that
            satisfy the search criteria an empty list is returned.

        """
        from akeyaa.stopwatch import stopwatch

        xycenter, radius = venue.circumcircle()
        candidates = self.fetch(xycenter, radius, aquifers)

        welldata = []
        for row in candidates:
            if venue.contains(row[0]):
                welldata.append(row)
        return welldata

    def get_well(self, relateid):
        """Get the welldata for a single well by relateid.

        Parameters
        ---------
        relateid : str
            The unique 10-digit well number encoded as a string with
            leading zeros.

            You can enter the relateid as an integer and this function
            will convert it to a string.

        Returns
        -------
        tuple : ((x, y), z, aquifer, relateid)
            If the relateid is found, return the associated complete welldata
            tuple. If the relateid is not found, return None.

        Notes
        -----
        The welldata is searched using a bisection algorithm, so it is fast.

        """
        if isinstance(relateid, int):
            relateid = f"{relateid:010d}"

        i = bisect_left(Wells.__relateid, relateid)
        if i == len(Wells.__relateid) or Wells.__relateid[i] != relateid:
            return None
        return Wells.__welldata[i]
