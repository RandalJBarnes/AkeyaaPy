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

Notes
-----
o   All of the classes in this module are of the informal type Venue.
    Although it is not enforced by subclassing, any venue must have
    the following methods:

    boundary(self): -> ndarray, shape=(n, 2), dtype= float
        Return the boundary vertices (domain to the left).

    extent(self) -> [float, float, float, float]
        Return [xmin, xmax, ymin, ymax] of the bounding axis-aligned rectangle.

    centroid(self) -> ndarray, shape=(2,), dtype=float
        Return the centroid as a point.

    area(self) -> float
        Return the area [m^2].

    perimeter(self) -> float
        Return the perimeter [m].

    contains(self, point) -> bool
        Return True if the Shape contains the point and False otherwise.

    fullname(self) -> str
        Return a form of the venue's name appropriate for a plot title.

    __eq__(self, other) -> bool
        Return True is the two venues are the same.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
05 June 2020
"""

import gis
from geometry import Circle, Polygon, Rectangle


# -----------------------------------------------------------------------------
class Error(Exception):
    """The base exception for the module. """

class MissingArgumentError(Error):
    """The call is missing one or more arguments. """

# -----------------------------------------------------------------------------
class City(Polygon):
    """City subclass of the Venue.

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

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"City of {self.name}"


# -----------------------------------------------------------------------------
class Township(Polygon):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"{self.name} Township"


# -----------------------------------------------------------------------------
class County(Polygon):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"{self.name} County"


# -----------------------------------------------------------------------------
class Watershed(Polygon):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"{self.name} Watershed"


# -----------------------------------------------------------------------------
class Subregion(Polygon):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"{self.name} Subregion"


# -----------------------------------------------------------------------------
class State(Polygon):
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

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"State of {self.name}"


# -----------------------------------------------------------------------------
class Neighborhood(Circle):
    """Neighborhood subclass of Venue.

    Attributes
    ----------
    name : str
        The neighborhood name.

    code : str, int
        If the Neighborhood is centered on a well, the unique RELATEID as
        defined in the CWI. This includes the initial zeros.

        For example, RELATEID = "0000457883".

        If the Neighborhood is centered on a user-defined point, the hash
        of the Circle's attributes: hash((point[0], point[1], radius)).

    center : ndarray, shape=(2,), dtype=float
        The [x, y] coordinates of the center point [m].

    radius : float
        The radius of the circle [m].
    """

    def __init__(self, *, relateid=None, point=None, radius=None, name=None):
        if radius is None:
            raise MissingArgumentError("A radius is required.")

        if relateid is not None:
            well_location = gis.get_well_location(relateid)
            point = well_location[0]

        elif point is None:
            raise MissingArgumentError("A relateid or point is required.")

        Circle.__init__(point, radius)

        if name is not None:
            self.name = name
        else:
            self.name = "Neighborhood"

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"center = {self.center}, "
                f"radius = {self.radius})")

    def __eq__(self, other):
        return (
                (self.__class__ == other.__class__) and
                (self.center == other.center) and
                (self.radius == other.radius))

    def fullname(self):
        return f"User Defined: {self.name}"


# -----------------------------------------------------------------------------
class Frame(Rectangle):
    """Neighborhood subclass of Venue.

    Attributes
    ----------
    name : str
        The neighborhood name.

    xmin : float
        The x coordinate of the left [m].

    xmax : float
        The x coordinate of the right [m].

    ymin : float
        The y coordinate of the bottom [m].

    ymax : float
        The y coordinate of the top [m].
    """

    def __init__(self, *, xmin=None, xmax=None, ymin=None, ymax=None, name=None):
        Rectangle.__init__(self, xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax)

        if name is not None:
            self.name = name
        else:
            self.name = "Frame"

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name = '{self.name}', "
                f"xmin = {self.xmin!r}, "
                f"xmax = {self.xmax!r}, "
                f"ymin = {self.ymin!r}, "
                f"ymax = {self.ymax!r})")

    def __eq__(self, other):
        return (
                (self.__class__ == other.__class__) and
                (self.xmin == other.xmin) and
                (self.xmax == other.xmax) and
                (self.ymin == other.ymin) and
                (self.ymax == other.ymax))

    def fullname(self):
        return f"User Defined: {self.name}"
