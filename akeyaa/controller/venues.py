"""Define and implement the Venue class and all of its subclasses.

A Venue is an instance of a political division, administrative region, or
user-defined domain, as enumerated and detailed in `akeyaa.venues`.
For example: a ``City``, ``Watershed``, or ``Neighborhood``.

Notes
-----
* Currently, there are eight unique types of venues.
    - City(Polygon)             political division
    - Township(Polygon)         political division
    - County(Polygon)           political division
    - Watershed(Polygon)        administrative region
    - Subregion(Polygon)        administrative region
    - Neighborhood(Circle)      user-defined domain
    - Frame(Rectangle)          user-defined domain

* All of the classes in this module are of the informal type Venue.
  But Venue is not a formal abstract base class. Nonetheless, any Venue must
  have the following methods in addition to all of the methods promised
  by the abstract base class geometry.Shape.

    __eq__(self, other) -> bool
        Return True is the two venues are the same.

    fullname(self) -> str
        Return a form of the venue's name appropriate for a plot title.

See Also
--------
akeyaa.geometry

"""
from akeyaa.controller.geometry import Circle, Polygon, Rectangle

__author__ = "Randal J Barnes"
__version__ = "10 August 2020"


class Error(Exception):
    """The base exception for the module."""


class MissingArgumentError(Error):
    """The call is missing one or more arguments."""


class ConflictingArgumentError(Error):
    """Two or more of the arguments are in conflict."""


class City(Polygon):
    """City venue by duck-type.

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

    def __init__(self, name, code, vertices):
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name = '{self.name}', "
            f"gnis_id = '{self.code}')"
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"City of {self.name}"


class Township(Polygon):
    """Township Venue-by-duck-type.

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

    def __init__(self, name, code, vertices):
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name = '{self.name}', "
            f"gnis_id = '{self.code}')"
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"{self.name} Township"


class County(Polygon):
    """County Venue-by-duck-type.

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

    def __init__(self, name, code, vertices):
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name = '{self.name}', "
            f"cty_fips = {self.code})"
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"{self.name} County"


class Watershed(Polygon):
    """Watershed Venue-by-duck-type.

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

    def __init__(self, name, code, vertices):
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name = '{self.name}', "
            f"huc10 = '{self.code}')"
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"{self.name} Watershed"


class Subregion(Polygon):
    """Subregion Venue-by-duck-type.

    Attributes
    ----------
    name : str
        The subregion name found in the .gdb.

    code : str
        The unique 8-digit hydrologic unit code (HUC8) encoded as a string.

        For example, Twin Cities subregion HUC8 = "07010206".

    vertices : ndarray, shape=(n, 2), dtype=float
        An array of vertices; i.e. a 2D numpy array of (x, y) corredinates [m].
        The vertices are stored so that the domain is on the left, and the
        first vertex is repeated as the last vertex.

    """

    def __init__(self, name, code, vertices):
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name = '{self.name}', "
            f"huc8 = '{self.code}')"
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"{self.name} Subregion"


class State(Polygon):
    """State Venue-by-duck-type.

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

    def __init__(self, name, code, vertices):
        self.name = name
        self.code = code
        Polygon.__init__(self, vertices)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name = '{self.name}', "
            f"fips = {self.code})"
        )

    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)

    def fullname(self):
        return f"State of {self.name}"


class Neighborhood(Circle):
    """Neighborhood Venue-by-duck-type.

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

    def __init__(self, name, point, radius):
        if name is not None:
            self.name = name
        else:
            self.name = "Neighborhood"
        Circle.__init__(point, radius)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name = '{self.name}', "
            f"center = {self.center}, "
            f"radius = {self.radius})"
        )

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__) and
            (self.center == other.center) and
            (self.radius == other.radius)
        )

    def fullname(self):
        return f"User Defined: {self.name}"


class Frame(Rectangle):
    """Rectangular frame Venue-by-duck-type.

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

    def __init__(
            self, name,
            xmin=None, xmax=None, ymin=None, ymax=None,
            lowerleft=None, width=None, height=None,
            upperright=None, center=None,
    ):
        """If specified,
            xmin, xmax, ymin, ymax, width, height -> float,
            lowerleft, upperright, center -> indexable (float, float).

        The rectangular frame may be specified one of five ways:
                [xmin, xmax, ymin, ymax]
                [lowerleft, width, height]
                [upperright, width, height]
                [lowerleft, upperright]
                [center, width, height]

        """
        if lowerleft is not None:
            xmin = lowerleft[0]
            ymin = lowerleft[1]
            if width is not None:
                xmax = lowerleft[0] + width
            if height is not None:
                ymax = lowerleft[1] + height

        if upperright is not None:
            xmax = upperright[0]
            ymax = upperright[1]
            if width is not None:
                xmin = upperright[0] - width
            if height is not None:
                ymin = upperright[1] - height

        if center is not None:
            xmin = center[0] - width / 2
            xmax = center[0] + width / 2
            ymin = center[1] - height / 2
            ymax = center[1] + height / 2

        Rectangle.__init__(self, xmin, xmax, ymin, ymax)

        if name is not None:
            self.name = name
        else:
            self.name = "Frame"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"name = '{self.name}', "
            f"xmin = {self.xmin}, "
            f"xmax = {self.xmax}, "
            f"ymin = {self.ymin}, "
            f"ymax = {self.ymax})"
        )

    def __eq__(self, other):
        return (
            (self.__class__ == other.__class__)
            and (self.xmin == other.xmin)
            and (self.xmax == other.xmax)
            and (self.ymin == other.ymin)
            and (self.ymax == other.ymax)
        )

    def fullname(self):
        return f"User Defined: {self.name}"
