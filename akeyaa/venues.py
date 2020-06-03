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
03 June 2020

"""

from abc import ABC

import gis


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

    polygon : geometry.Polygon
        The city boundary.
    """

    def __init__(self, *, name=None, gnis_id=None):
        self.name, self.code, self.polygon = gis.get_city_data(name, gnis_id)

    def __repr__(self):
        return f"{self.__class__.__name__}(name = {self.name}, gnis_id = {self.code})"

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

    polygon : geometry.Polygon
        The township boundary.
    """

    def __init__(self, *, name=None, gnis_id=None):
        self.name, self.code, self.polygon = gis.get_township_data(
                name=name, gnis_id=gnis_id)

    def __repr__(self):
        return f"{self.__class__.__name__}(name = {self.name}, gnis_id = {self.code})"

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

    polygon : geometry.Polygon
        The county boundary.
    """

    def __init__(self, *, name=None, abbr=None, cty_fips=None):
        self.name, self.code, self.polygon = gis.get_county_data(
                name=name, abbr=abbr, cty_fips=cty_fips)

    def __repr__(self):
        return f"{self.__class__.__name__}(name = {self.name}, cty_fips = {self.code})"

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

    polygon : geometry.Polygon
        The watershed boundary.
    """

    def __init__(self, *, name=None, huc10=None):
        self.name, self.code, self.polygon = gis.get_watershed_data(
                name=name, huc10=huc10)

    def __repr__(self):
        return f"{self.__class__.__name__}(name = {self.name}, huc10 = {self.code})"

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

    polygon : geometry.Polygon
        The subregion boundary.
    """

    def __init__(self, *, name=None, huc8=None):
        self.name, self.code, self.polygon = gis.get_subregion_data(
                name=name, huc8=huc8)

    def __repr__(self):
        return f"{self.__class__.__name__}(name = {self.name}, huc8 = {self.code})"

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

    polygon : geometry.Polygon
        The watershed boundary.
    """

    def __init__(self):
        self.name, self.code, self.polygon = gis.get_state_data()

    def __repr__(self):
        return f"{self.__class__.__name__}(name = {self.name},  fips = {self.code})"

    def fullname(self):
        return f"State of {self.name}"
