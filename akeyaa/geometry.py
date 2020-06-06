"""Simple geometric shape classes: Circle, Rectangle, and Polygon.

Classes
-------
Shape(ABC)
    The abstract base class for all Shapes.

Circle(Shape)
    A circle.

Rectangle(Shape)
    An axis-aligned rectangle.

Polygon(Shape)
    A single, non-overlapping, but not necessarily convex, polygon.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
06 June 2020
"""

from abc import ABC, abstractmethod
import numpy as np


#-----------------------------------------------------------------------------------------
class Shape(ABC):
    """The abstract base class for all shapes.

    For the purposes of a Shape:
    -- a <point> is a numpy.array([x, y], dtype=float),
    -- <vertices> is a numpy.array of points (i.e. a 2D array).
    """

    @abstractmethod
    def __eq__(self, other):
        """Return True if the two Shapes are equal."""
        raise NotImplementedError

    @abstractmethod
    def boundary(self):
        """Return the boundary vertices (domain to the left)."""
        raise NotImplementedError

    @abstractmethod
    def extent(self):
        """Return [xmin, xmax, ymin, ymax] of the bounding axis-aligned rectangle."""
        raise NotImplementedError

    @abstractmethod
    def centroid(self):
        """Return the centroid as a point."""
        raise NotImplementedError

    @abstractmethod
    def area(self):
        """Return the area [m^2]."""
        raise NotImplementedError

    @abstractmethod
    def perimeter(self):
        """Return the perimeter [m]."""
        raise NotImplementedError

    @abstractmethod
    def contains(self, point):
        """Return True if the Shape contains the point and False otherwise."""
        raise NotImplementedError


#-----------------------------------------------------------------------------------------
class Circle(Shape):
    """A circle.

    Attributes
    ----------
    center : ndarray, shape=(2,), dtype=float
        The [x, y] coordinates of the center point [m].

    radius : float
        The radius of the circle [m].
    """

    NUMBER_OF_VERTICES = 100
    UNIT_VERTICES = np.array([(np.cos(theta), np.sin(theta))
        for theta in np.linspace(0, 2*np.pi, NUMBER_OF_VERTICES)], dtype=float)

    def __init__(self, center, radius):
        self.center = np.array([center[0], center[1]], dtype=float)
        self.radius = float(radius)

    def __repr__(self):
        return (
                f"{self.__class__.__name__}("
                f"center = {self.center!r}, "
                f"radius = {self.radius!r})"
        )

    def __str__(self):
        return (
                f"Circle: "
                f"[{self.center[0]}, "
                f"{self.center[1]}], "
                f"{self.radius}"
       )

    def __eq__(self, other):
        """Return True if the two Circle are equal."""
        return ((self.__class__ == other.__class__) and
                (self.center == other.center) and
                (self.radius == other.radius))

    def boundary(self):
        """Return the boundary vertices (domain to the left)."""
        return Circle.UNIT_VERTICES*self.radius + self.center

    def extent(self):
        """Return [xmin, xmax, ymin, ymax] of the bounding axis-aligned rectangle."""
        return [self.center[0]-self.radius,
                self.center[0]+self.radius,
                self.center[1]-self.radius,
                self.center[1]+self.radius]

    def centroid(self):
        """Return the centroid as a point."""
        return self.center

    def area(self):
        """Return the area [m^2]."""
        return np.pi * self.radius**2

    def perimeter(self):
        """Return the perimeter [m]."""
        return 2*np.pi * self.radius

    def contains(self, point):
        """Return True if the Circle contains the point and False otherwise."""
        return np.hypot(point[0]-self.center[0], point[1]-self.center[1]) < self.radius


#-----------------------------------------------------------------------------------------
class Rectangle(Shape):
    """An axis-aligned rectangle.

    Attributes
    ----------
    xmin : float
        The x coordinate of the left [m].

    xmax : float
        The x coordinate of the right [m].

    ymin : float
        The y coordinate of the bottom [m].

    ymax : float
        The y coordinate of the top [m].
    """

    def __init__(self, xmin, xmax, ymin, ymax):
        self.xmin = float(xmin)
        self.xmax = float(xmax)
        self.ymin = float(ymin)
        self.ymax = float(ymax)

    def __repr__(self):
        return (
                f"{self.__class__.__name__}("
                f"xmin = {self.xmin!r}, "
                f"xmax = {self.xmax!r}, "
                f"ymin = {self.ymin!r}, "
                f"ymax = {self.ymax!r})")

    def __str__(self):
        return (
                f"Rectangle: "
                f"[{self.xmin}, {self.xmax}, {self.ymin}, {self.ymax}]")

    def __eq__(self, other):
        """Return True if the two Rectangles are equal."""
        return ((self.__class__ == other.__class__) and
                (self.xmin == other.xmin) and
                (self.xmax == other.xmax) and
                (self.ymin == other.ymin) and
                (self.ymax == other.ymax))

    def boundary(self):
        """Return the boundary vertices (domain to the left)."""
        return np.array([
                [self.xmin, self.ymin],
                [self.xmax, self.ymin],
                [self.xmax, self.ymax],
                [self.xmin, self.ymax],
                [self.xmin, self.ymin]
                ], dtype=float)

    def extent(self):
        """Return [xmin, xmax, ymin, ymax] of the bounding axis-aligned rectangle."""
        return [self.xmin, self.xmax, self.ymin, self.ymax]

    def centroid(self):
        """Return the centroid as a point."""
        return np.array([(self.xmax+self.xmin)/2, (self.ymax+self.ymin)/2], dtype=float)

    def area(self):
        """Return the area [m^2]."""
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)

    def perimeter(self):
        """Return the perimeter [m]."""
        return 2*(self.xmax - self.xmin) + 2*(self.ymax - self.ymin)

    def contains(self, point):
        """Return True if the Rectangle contains the point and False otherwise."""
        return (self.xmin < point[0] < self.xmax) and (self.ymin < point[1] < self.ymax)


#-----------------------------------------------------------------------------------------
class Polygon(Shape):
    """A single, non-overlapping, but not necessarily convex, polygon.

    Attributes
    ----------
    vertices : ndarray, shape=(n, 2), dtype=float
        An array of vertices; i.e. a 2D numpy array of (x, y) corredinates [m].
        The vertices are stored so that the domain is on the left, and the
        first vertex is repeated as the last vertex.
    """

    def __init__(self, vertices):
        self.vertices = vertices

        if self.area() < 0:
            self.vertices = np.flipud(self.vertices)

    def __repr__(self):
        return f"{self.__class__.__name__}(vertices = {self.vertices})"

    def __str__(self):
        return "Polygon: [...]"

    def __eq__(self, other):
        """Return True if the two Polygons are equal."""
        return ((self.__class__ == other.__class__) and
                (self.vertices == other.vertices))

    def boundary(self):
        """Return the boundary vertices (domain to the left)."""
        return self.vertices

    def extent(self):
        """Return [xmin, xmax, ymin, ymax] of the bounding axis-aligned rectangle."""
        xmin, ymin = np.min(self.vertices, axis=0)
        xmax, ymax = np.max(self.vertices, axis=0)
        return [xmin, xmax, ymin, ymax]

    def centroid(self):
        """Return the centroid as a point."""
        x = self.vertices[:, 0]
        y = self.vertices[:, 1]

        cx = 0.0
        cy = 0.0

        for i in range(len(self.vertices)-1):
            cx += (x[i]+x[i+1]) * (x[i]*y[i+1] - x[i+1]*y[i])
            cy += (y[i]+y[i+1]) * (x[i]*y[i+1] - x[i+1]*y[i])

        area = self.area()
        cx /= (6*area)
        cy /= (6*area)
        return np.array([cx, cy], dtype=float)

    def area(self):
        """Return the area [m^2]."""
        x = self.vertices[:, 0]
        y = self.vertices[:, 1]

        area = 0.0
        for i in range(len(self.vertices)-1):
            area += x[i]*y[i+1] - x[i+1]*y[i]
        area /= 2
        return area

    def perimeter(self):
        """Return the perimeter [m]."""
        x = self.vertices[:, 0]
        y = self.vertices[:, 1]

        length = 0.0
        for i in range(len(self.vertices)-1):
            length += np.hypot(x[i+1]-x[i], y[i+1]-y[i])
        return length

    def contains(self, point):
        """Return True if the Polygon contains the point and False otherwise."""
        inside = False
        xa, ya = self.vertices[0]

        for i in range(len(self.vertices)):
            xb, yb = self.vertices[i]
            if point[1] > min(ya, yb):
                if point[1] <= max(ya, yb):
                    if point[0] <= max(xa, xb):
                        if ya != yb:
                            xints = (point[1]-ya)*(xb-xa)/(yb-ya) + xa
                        if xa == xb or point[0] <= xints:
                            inside = not inside
            xa, ya = xb, yb
        return inside
