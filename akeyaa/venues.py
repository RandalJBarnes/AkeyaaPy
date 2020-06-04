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
04 June 2020

"""

from abc import ABC

import gis
import geometry


# -----------------------------------------------------------------------------
class Error(Exception):
    """The base exception for the module. """

class MissingArgumentError(Error):
    """The call is missing one or more arguments. """


# -----------------------------------------------------------------------------
class Venue(ABC):
    """The abstract base class for all venues."""

    # -----------------------
    def __eq__(self, other):
        return (self.__class__ == other.__class__) and (self.code == other.code)


# -----------------------------------------------------------------------------
class City(Venue):
    """City subclass of Venue.

    Attributes
    ----------
    name : str

    code : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

        For example, City of Hugo GNIS = "2394440".

    domain : geometry.Domain
        The city boundary.
    """

    def __init__(self, *, name=None, gnis_id=None):
        self.name, self.code, vertices = gis.get_city_data(
                name=name, gnis_id=gnis_id)
        self.domain = geometry.Polygon(vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}(name = '{self.name}', "
                f"gnis_id = '{self.code}')")

    def fullname(self):
        return f"City of {self.name}"


# -----------------------------------------------------------------------------
class Township(Venue):
    """Township subclass of Venue.

    Attributes
    ----------
    name : str

    code : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

        For example, White Bear Township GNIS = "665981".

    domain : geometry.Domain
        The township boundary.
    """

    def __init__(self, *, name=None, gnis_id=None):
        self.name, self.code, vertices = gis.get_township_data(
                name=name, gnis_id=gnis_id)
        self.domain = geometry.Polygon(vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}(name = '{self.name}', "
                f"gnis_id = '{self.code}')")

    def fullname(self):
        return f"{self.name} Township"


# -----------------------------------------------------------------------------
class County(Venue):
    """County subclass of Venue.

    Attributes
    ----------
    name : str

    code : int
        The unique 5-digit Federal Information Processing Standards code
        (FIPS), without the initial 2 digits state code.

        For example, Washington County FIPS = 163

    domain : geometry.Domain
        The county boundary.
    """

    def __init__(self, *, name=None, abbr=None, cty_fips=None):
        self.name, self.code, vertices = gis.get_county_data(
                name=name, abbr=abbr, cty_fips=cty_fips)
        self.domain = geometry.Polygon(vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}(name = '{self.name}', "
                f"cty_fips = {self.code})")

    def fullname(self):
        return f"{self.name} County"


# -----------------------------------------------------------------------------
class Watershed(Venue):
    """Watershed subclass of Venue.

    Attributes
    ----------
    name : str

    code : str
        The unique 10-digit hydrologic unit code (HUC10) encoded as a
        string.

        For example, Sunrise River Watershed HUC10 = "0703000504".

    domain : geometry.Domain
        The watershed boundary.
    """

    def __init__(self, *, name=None, huc10=None):
        self.name, self.code, vertices = gis.get_watershed_data(
                name=name, huc10=huc10)
        self.domain = geometry.Polygon(vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}(name = '{self.name}', "
                f"huc10 = '{self.code}')")

    def fullname(self):
        return f"{self.name} Watershed"


# -----------------------------------------------------------------------------
class Subregion(Venue):
    """Subregion subclass of Venue.

    Attributes
    ----------
    name : str

    code : str
        The unique 8-digit hydrologic unit code (HUC10) encoded as a
        string.

        For example, Twin Cities subregion HUC8 = "07010206".

    domain : geometry.Domain
        The subregion boundary.
    """

    def __init__(self, *, name=None, huc8=None):
        self.name, self.code, vertices = gis.get_subregion_data(
                name=name, huc8=huc8)
        self.domain = geometry.Polygon(vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}(name = '{self.name}', "
                f"huc8 = '{self.code}')")

    def fullname(self):
        return f"{self.name} Subregion"


# -----------------------------------------------------------------------------
class State(Venue):
    """State subclass of Venue.

    Attributes
    ----------
    name : str

    code : int
        The intial 2 digits of the unique 5-digit Federal Information
        Processing Standards code -- i.e. the state FIPS code.

        For example, The FIPS code for Minnesota = 27.

    domain : geometry.Domain
        The watershed boundary.
    """

    def __init__(self):
        self.name, self.code, vertices = gis.get_state_data()
        self.domain = geometry.Polygon(vertices)

    def __repr__(self):
        return (f"{self.__class__.__name__}(name = '{self.name}', "
                f"fips = {self.code})")

    def fullname(self):
        return f"State of {self.name}"


# -----------------------------------------------------------------------------
class Neighborhood(Venue):
    """Neighborhood subclass of Venue.

    Attributes
    ----------
    name : str

    code : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

        For example, City of Hugo GNIS = "2394440".

    domain : geometry.Domain
        The city boundary.
    """

    def __init__(self, radius, *, relateid=None, point=None):
        if relateid is not None:
            well_location = gis.get_well_location(relateid)
            self.name = f"Well"
            self.point = well_location[0]
            self.code = relateid
            self.fname = f"Well '{relateid}'"

        elif point is not None:
            self.name = f"Point"
            self.point = point
            self.code = hash(point)
            self.fname = f"Point {self.point}"

        else:
            raise MissingArgumentError("A relateid or point is required.")

        self.radius = radius
        self.domain = geometry.Circle(self.point, self.radius)

    def __repr__(self):
        return (f"{self.__class__.__name__}(name = '{self.name}', "
                f"code = '{self.code}', "
                f"point = {self.point}, radius = {self.radius})")

    def fullname(self):
        return self.fname
