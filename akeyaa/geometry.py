"""Simple geometric shape classes: Circle, Rectangle, and Polygon.

Classes
-------


Functions
---------


Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
03 June 2020

"""
import numpy as np


#-----------------------------------------------------------------------------------------
class Circle():
    """A circle."""

    NUMBER_OF_VERTICES = 100
    UNIT_VERTICES = np.array([(np.cos(theta), np.sin(theta))
        for theta in np.linspace(0, 2*np.pi, NUMBER_OF_VERTICES)], dtype=float)

    def __init__(self, origin, radius):
        self.origin = np.array([origin[0], origin[1]], dtype=float)
        self.radius = float(radius)

    def __repr__(self):
        return (
                f"{self.__class__.__name__}("
                f"origin = {self.origin!r}, "
                f"radius = {self.radius!r})"
        )

    def __str__(self):
        return (
                f"Circle: "
                f"[{self.origin[0]}, "
                f"{self.origin[1]}], "
                f"{self.radius}"
       )

    def boundary(self):
        return Circle.UNIT_VERTICES*self.radius + self.origin

    def extent(self):
        return [self.origin[0]-self.radius,
                self.origin[0]+self.radius,
                self.origin[1]-self.radius,
                self.origin[1]+self.radius]

    def centroid(self):
        return self.origin

    def area(self):
        return np.pi * self.radius**2

    def perimeter(self):
        return 2*np.pi * self.radius

    def contains(self, point):
        return np.hypot(point[0]-self.origin[0], point[1]-self.origin[1]) < self.radius


#-----------------------------------------------------------------------------------------
class Rectangle():
    """An axis-aligned rectangle."""

    def __init__(self, xmin, xmax, ymin, ymax, name):
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
                f"ymax = {self.ymax!r})"
        )

    def __str__(self):
        return (
                f"Rectangle: "
                f"[{self.xmin}, {self.xmax}, {self.ymin}, {self.ymax}] "
        )

    def boundary(self):
        return np.array([
                [self.xmin, self.ymin],
                [self.xmax, self.ymin],
                [self.xmax, self.ymax],
                [self.xmin, self.ymax],
                [self.xmin, self.ymin]
                ], dtype=float)

    def extent(self):
        return [self.xmin, self.xmax, self.ymin, self.ymax]

    def centroid(self):
        return np.array([(self.xmax+self.xmin)/2, (self.ymax+self.ymin)/2], dtype=float)

    def area(self):
        return (self.xmax - self.xmin) * (self.ymax - self.ymin)

    def perimeter(self):
        return 2*(self.xmax - self.xmin) + 2*(self.ymax - self.ymin)

    def contains(self, point):
        return (self.xmin < point[0] < self.xmax) and (self.ymin < point[1] < self.ymax)


#-----------------------------------------------------------------------------------------
class Polygon:
    """A single, non-overlapping, but not necessarily convex, polygon."""

    def __init__(self, vertices):
        self.vertices = vertices

        if self.area() < 0:
            self.vertices = np.flipud(self.vertices)

    def __repr__(self):
        return f"{self.__class__.__name__}(vertices = {self.vertices})"

    def __str__(self):
        return "Polygon: [...]"

    def boundary(self):
        return self.vertices

    def extent(self):
        xmin, ymin = np.min(self.vertices, axis=0)
        xmax, ymax = np.max(self.vertices, axis=0)
        return [xmin, xmax, ymin, ymax]

    def centroid(self):
        x = self.vertices[:, 0]
        y = self.vertices[:, 1]

        cx = 0.0;
        cy = 0.0

        for i in range(len(self.vertices)-1):
            cx += (x[i]+x[i+1]) * (x[i]*y[i+1] - x[i+1]*y[i])
            cy += (y[i]+y[i+1]) * (x[i]*y[i+1] - x[i+1]*y[i])

        area = self.area()
        cx /= (6*area)
        cy /= (6*area)
        return np.array([cx, cy], dtype=float)

    def area(self):
        x = self.vertices[:, 0]
        y = self.vertices[:, 1]

        area = 0.0
        for i in range(len(self.vertices)-1):
            area += x[i]*y[i+1] - x[i+1]*y[i]
        area /= 2
        return area

    def perimeter(self):
        x = self.vertices[:, 0]
        y = self.vertices[:, 1]

        length = 0.0
        for i in range(len(self.vertices)-1):
            length += np.hypot(x[i+1]-x[i], y[i+1]-y[i])
        return length

    def contains(self, point):
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
