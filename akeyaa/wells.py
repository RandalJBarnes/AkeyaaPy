"""Define and implement the wells database.

Extract all of the necessary well data from the .gdb, and create an
associated database for very fast lookup based on coordinates or relateid.

"""
from bisect import bisect_left
from itertools import compress
from operator import itemgetter
import scipy


from akeyaa.gis import get_all_well_data

__author__ = "Randal J Barnes"
__version__ = "24 July 2020"


class Wells(object):
    """Create and manage the in-memory, python-based, well database.

    Attributes
    ----------
    __welldata : list[tuple] (xy, z, aquifer, relateid)
        xy : tuple (float, float)
            The x- and y-coordinates in "NAD 83 UTM 15N" (EPSG:26915) [m].

        z : float
            The recorded static water level [ft]

        aquifer : str
            The 4-character aquifer abbreviation string, as defined in
            Minnesota Geologic Survey's coding system.

        relateid : str
            The unique 10-digit well number encoded as a string with
            leading zeros.

        date : int
            Recorded measurement date writeen as YYYYMMDD.

        For example: ((232372.0, 5377518.0), 964.0, 'QBAA', '0000153720', '19650322')

    __relateid : list[str]
        The unique 10-digit well number encoded as a string with leading
        zeros. This is a duplicate of the field realteid in __welldata to
        be used as a search key.

    __tree : scipy.spatial.cKDTree
        A kd-tree for all of the wells in fetch.welldata.

    Notes
    -----
    *   The welldata list contains data from all authorized wells taken across
        the state. Wells that have multiple static water level measurements
        will have multiple entries in this table -- one entry for every
        measurement.

    *   The welldata is sorted in ascending order by the relateid to allow for
        quick searches on the relateid using the bisect tools.

    *   The __relateid list is created as a search key.

    See Also
    --------
    akeyaa.wells

    """
    __welldata = None
    __relateid = None
    __tree = None


    @classmethod
    def initialize(cls):
        """Initialize the class attributes.

        Initialize __welldata, __relateid, and __tree.  Specifically, extract
        the well data from an external .gdb, setup the kd search tree, and
        sort id list.

        """
        if cls.__welldata is None:
            cls.__welldata = sorted(get_all_well_data(), key=itemgetter(3))
            cls.__relateid = [row[3] for row in cls.__welldata]
            cls.__tree = scipy.spatial.cKDTree([row[0] for row in cls.__welldata])

    def __init__(self):
        """Setup the data and kd-tree in memory.

        Notes
        -----
        The first call is slow (a few seconds) because this calls the class
        initialize. Every call after the first is very fast.

        """
        if Wells.__welldata is None:
            Wells.initialize()

    def fetch(self, xytarget, radius, aquifers, before, after):
        """Fetch the nearby wells.

        Fetch the welldata for all authorized wells within `radius` of the
        coordinates `xytarget`, that are completed in one or more of the
        identified `aquifers`, and that have a measured date between `after`
        and `before`.

        Parameters
        ----------
        xytarget : tuple(float, float)
            x-coordinate (easting) and y-coordinate (northing) of the target
            location in NAD 83 UTM zone 15N [m].

        radius : float
            The radius of the search neighborhood [m].

        aquifers : list[str]
            List of four-character aquifer abbreviation strings, as defined in
            Minnesota Geologic Survey's coding system. If None, then wells
            from all aquifers will be included.

        after : int

        before : int

        Returns
        -------
        list[tuple] : (xy, z, aquifer, relateid, meas_date)
            Returns a list of tuples (see welldata above), with one tuple for
            each welldata entry that satisfies the search criteria. If there
            are no wells that satisfy the search criteria an empty list is
            returned.

        Notes
        -----
        * Beware! The x and y coordinates are in [m], but z is in [ft].

        """
        welldata = []
        indx = Wells.__tree.query_ball_point(xytarget, radius)
        if indx:
            for i in indx:
                if (
                    ((aquifers is None) or (Wells.__welldata[i][2] in aquifers)) and
                    ((after is None) or (Wells.__welldata[i][4] >= after)) and
                    ((before is None) or (Wells.__welldata[i][4] <= before))
                ):
                    welldata.append(Wells.__welldata[i])
        return welldata

    def fetch_by_venue(self, venue, aquifers, after, before):
        """Fetch wells in the specified venue.

        Fetch the welldata for all authorized wells that are completed in one
        or more of the identified `aquifers`, and that have a measured date
        between `after` and `before`.

        Parameters
        ----------
        venue: type
            An instance of a political division, administrative region, or
            user-defined domain, as enumerated and detailed in `akeyaa.venues`.
            For example: a ``City``, ``Watershed``, or ``Neighborhood``.

        aquifers : list[str]
            List of four-character aquifer abbreviation strings, as defined in
            Minnesota Geologic Survey's coding system. If None, then wells from
            all aquifers will be included.

        after : int
            Earliest measurement date to use; written as YYYYMMDD.

        before : int
            Latest measurement date to use; written as YYYYMMDD.

        Returns
        -------
        list[tuple] : (xy, z, aquifer, relateid)
            Returns a list of tuples (see welldata above), with one tuple for
            each welldata entry that satisfies the search criteria. If there
            are no wells that satisfy the search criteria an empty list is
            returned.

        """
        xycenter, radius = venue.circumcircle()
        candidates = self.fetch(xycenter, radius, aquifers, after, before)

        if candidates:
            flag = venue.contains_points([row[0] for row in candidates])
            return list(compress(candidates, flag))
        return []

    def get_well(self, relateid):
        """Get the welldata for a single well by relateid.

        Parameters
        ---------
        relateid : str, int
            The unique 10-digit well number encoded as a string with
            leading zeros.

            You can enter the relateid as an integer and this function
            will convert it to a string with the leading zeros.

        Returns
        -------
        tuple : (xy, z, aquifer, relateid)
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
