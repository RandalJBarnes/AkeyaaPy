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


Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
05 June 2020
"""

from abc import ABC, abstractmethod

import gis
from geometry import Circle, Polygon


# -----------------------------------------------------------------------------
class Error(Exception):
    """The base exception for the module. """

class MissingArgumentError(Error):
    """The call is missing one or more arguments. """


# -----------------------------------------------------------------------------
class Venue(ABC):
    """The abstract base class for all venues."""

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    @abstractmethod
    def fullname(self):
        raise NotImplementedError


# -----------------------------------------------------------------------------
class City(Venue, Polygon):
    """City subclass of Venue.

    Attributes
    ----------
    name : str
        The city name found in the .gdb.

    code : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

        For example, City of Hugo GNIS = "2394440".

    vertices : ndarray, shape=(n, 2), dtype=float
        An array of vertices; i.e. a 2D numpy array of (x, y) corredinates [m].
        The vertices are stored so that the domain is on the left, and the
        first vertex is repeated as the last vertex.
    """

    def __init__(self, *, name=None, gnis_id=None):
        name, code, vertices = gis.get_city_data(name=name, gnis_id=gnis_id)
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"gnis_id = '{self.code}')")

    def fullname(self):
        return f"City of {self.name}"


# -----------------------------------------------------------------------------
class Township(Venue, Polygon):
    """Township subclass of Venue.

    Attributes
    ----------
    name : str
        The township name found in the .gdb.

    code : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

        For example, White Bear Township GNIS = "665981".

    vertices : ndarray, shape=(n, 2), dtype=float
        An array of vertices; i.e. a 2D numpy array of (x, y) corredinates [m].
        The vertices are stored so that the domain is on the left, and the
        first vertex is repeated as the last vertex.
    """

    def __init__(self, *, name=None, gnis_id=None):
        name, code, vertices = gis.get_township_data(name=name, gnis_id=gnis_id)
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"gnis_id = '{self.code}')")

    def fullname(self):
        return f"{self.name} Township"


# -----------------------------------------------------------------------------
class County(Venue, Polygon):
    """County subclass of Venue.

    Attributes
    ----------
    name : str
        The county name found in the .gdb.

    code : int
        The unique 5-digit Federal Information Processing Standards code
        (FIPS), without the initial 2 digits state code.

        For example, Washington County FIPS = 163

    vertices : ndarray, shape=(n, 2), dtype=float
        An array of vertices; i.e. a 2D numpy array of (x, y) corredinates [m].
        The vertices are stored so that the domain is on the left, and the
        first vertex is repeated as the last vertex.
    """

    def __init__(self, *, name=None, abbr=None, cty_fips=None):
        name, code, vertices = gis.get_county_data(name=name, abbr=abbr, cty_fips=cty_fips)
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"cty_fips = {self.code})")

    def fullname(self):
        return f"{self.name} County"


# -----------------------------------------------------------------------------
class Watershed(Venue, Polygon):
    """Watershed subclass of Venue.

    Attributes
    ----------
    name : str
        The watershed name found in the .gdb.

    code : str
        The unique 10-digit hydrologic unit code (HUC10) encoded as a
        string.

        For example, Sunrise River Watershed HUC10 = "0703000504".

    vertices : ndarray, shape=(n, 2), dtype=float
        An array of vertices; i.e. a 2D numpy array of (x, y) corredinates [m].
        The vertices are stored so that the domain is on the left, and the
        first vertex is repeated as the last vertex.
    """

    def __init__(self, *, name=None, huc10=None):
        name, code, vertices = gis.get_watershed_data(name=name, huc10=huc10)
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"huc10 = '{self.code}')")

    def fullname(self):
        return f"{self.name} Watershed"


# -----------------------------------------------------------------------------
class Subregion(Venue, Polygon):
    """Subregion subclass of Venue.

    Attributes
    ----------
    name : str
        The subregion name found in the .gdb.

    code : str
        The unique 8-digit hydrologic unit code (HUC10) encoded as a
        string.

        For example, Twin Cities subregion HUC8 = "07010206".

    vertices : ndarray, shape=(n, 2), dtype=float
        An array of vertices; i.e. a 2D numpy array of (x, y) corredinates [m].
        The vertices are stored so that the domain is on the left, and the
        first vertex is repeated as the last vertex.
    """

    def __init__(self, *, name=None, huc8=None):
        name, code, vertices = gis.get_subregion_data(name=name, huc8=huc8)
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"huc8 = '{self.code}')")

    def fullname(self):
        return f"{self.name} Subregion"


# -----------------------------------------------------------------------------
class State(Venue, Polygon):
    """State subclass of Venue.

    Attributes
    ----------
    name : str
        The state name found in the .gdb.

    code : int
        The intial 2 digits of the unique 5-digit Federal Information
        Processing Standards code -- i.e. the state FIPS code.

        For example, The FIPS code for Minnesota = 27.

    vertices : ndarray, shape=(n, 2), dtype=float
        An array of vertices; i.e. a 2D numpy array of (x, y) corredinates [m].
        The vertices are stored so that the domain is on the left, and the
        first vertex is repeated as the last vertex.
    """

    def __init__(self):
        name, code, vertices = gis.get_state_data()
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"fips = {self.code})")

    def fullname(self):
        return f"State of {self.name}"


# -----------------------------------------------------------------------------
class Neighborhood(Venue, Circle):
    """Neighborhood subclass of Venue.

    Attributes
    ----------
    name : str
        The neighborhood name.

    code : str
        If the Neighborhood is centered on a well, the unique RELATEID as
        defined in the CWI. This includes the initial zeros.

        For example, RELATEID = "0000457883".

        If the Neighborhood is centered on a user-defined point, the hash
        of the stringified center point: str(hash(str(center))).

        For example, code = '8794749961149465368'.

    center : ndarray, shape=(2,), dtype=float
        The [x, y] coordinates of the center point [m].

    radius : float
        The radius of the circle [m].
    """

    def __init__(self, radius, *, relateid=None, point=None):
        if relateid is not None:
            well_location = gis.get_well_location(relateid)
            point = well_location[0]
            self.name = "Well"
            self.code = relateid
            self.fullname = f"Well '{relateid}'"

        elif point is not None:
            self.name = "Point"
            self.code = str(hash(str(self.center)))
            self.fullname = f"center {self.center}"

        else:
            raise MissingArgumentError("A relateid or center is required.")

        Circle.__init__(point, radius)

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"code = '{self.code}', "
                f"center = {self.center}, "
                f"radius = {self.radius})")

    def fullname(self):
        return self.fullname
