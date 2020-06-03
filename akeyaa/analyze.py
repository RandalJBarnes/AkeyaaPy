"""The functions to carry out the actual Akeyaa analysis.

Classes
-------
Settings
    A dataclass for the Akeyaa analysis settings.

Functions
---------
akeyaa_settings(aquifers, method, radius, required, spacing)
    Create a dictionary with a complete set of valid settings.

by_venue(venue, database, settings)
    Compute the Akeyaa analysis across the specified venue.

by_polygon(polygon, database, settings)
    Compute the Akeyaa analysis across the specified polygon.

layout_the_grid(polygon, spacing)
    Determine the locations of the x and y grid lines.

fit_conic(x, y, z, method)
    Fit the local conic potential model to the selected heads.

Raises
------
ValueError

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
01 June 2020
"""

import numpy as np
import statsmodels.api as sm

import wells


# -----------------------------------------------------------------------------
# These are the default settings for the Akeyaa analysis. TODO: revisit these
# default values after we have more exprience.
DEFAULT_AQUIFERS = None
DEFAULT_METHOD = "RLM"
DEFAULT_RADIUS = 3000
DEFAULT_REQUIRED = 25
DEFAULT_SPACING = 1000


# -----------------------------------------------------------------------------
# The following is a complete list of all 4-character aquifer codes used in
# the Minnesota County Well index as of 1 January 2020.
ALL_AQUIFERS = {
    "CAMB", "CECR", "CEMS", "CJDN", "CJDW", "CJMS", "CJSL", "CJTC", "CLBK",
    "CMFL", "CMRC", "CMSH", "CMTS", "CSLT", "CSLW", "CSTL", "CTCE", "CTCG",
    "CTCM", "CTCW", "CTLR", "CTMZ", "CWEC", "CWMS", "CWOC",
    "DCLP", "DCLS", "DCOG", "DCOM", "DCVA", "DCVL", "DCVU", "DEVO", "DPOG",
    "DPOM", "DSOG", "DSOM", "DSPL", "DWAP", "DWPR",
    "INDT", "KDNB", "KREG", "KRET", "MTPL",
    "ODCR", "ODGL", "ODPL", "ODUB", "OGCD", "OGCM", "OGDP", "OGPC", "OGPD",
    "OGPR", "OGSC", "OGSD", "OGSV", "OGVP", "OGWD", "OMAQ", "OMQD", "OMQG",
    "OPCJ", "OPCM", "OPCT", "OPCW", "OPDC", "OPGW", "OPNR", "OPOD", "OPSH",
    "OPSP", "OPVJ", "OPVL", "OPWR", "ORDO", "ORRV", "OSCJ", "OSCM", "OSCS",
    "OSCT", "OSPC", "OSTP", "OWIN",
    "PAAI", "PAAM", "PABD", "PABG", "PABK", "PACG", "PAEF", "PAES", "PAEY",
    "PAFL", "PAFR", "PAFV", "PAGR", "PAGU", "PAJL", "PAKG", "PALC", "PALG",
    "PALL", "PALP", "PALS", "PALT", "PALV", "PAMB", "PAMC", "PAMD", "PAMG",
    "PAML", "PAMR", "PAMS", "PAMT", "PAMU", "PAMV", "PANB", "PANL", "PANS",
    "PANU", "PAOG", "PAQF", "PASG", "PASH", "PASL", "PASM", "PASN", "PASR",
    "PAST", "PASZ", "PATL", "PAUD", "PAVC", "PAWB", "PCCR", "PCRG", "PCUU",
    "PEAG", "PEAL", "PEBC", "PEBI", "PEDN", "PEDQ", "PEFG", "PEFH", "PEFM",
    "PEGT", "PEGU", "PEHL", "PEIL", "PELF", "PELR", "PEMG", "PEML", "PEMN",
    "PEMU", "PEPG", "PEPK", "PEPP", "PEPZ", "PERB", "PERF", "PERV", "PESC",
    "PEST", "PESX", "PETR", "PEUD", "PEVT", "PEWR", "PEWT", "PEWV", "PMBB",
    "PMBE", "PMBI", "PMBL", "PMBM", "PMBO", "PMBR", "PMCV", "PMDA", "PMDC",
    "PMDE", "PMDF", "PMDL", "PMEP", "PMES", "PMFL", "PMGI", "PMGL", "PMHF",
    "PMHN", "PMHR", "PMLD", "PMMU", "PMNF", "PMNI", "PMNL", "PMNM", "PMNS",
    "PMPA", "PMRC", "PMSU", "PMTH", "PMUD", "PMUS", "PMVU", "PMWL", "PUDF",
    "QBAA", "QBUA", "QUUU", "QWTA", "RUUU", "UREG"
    }


# -----------------------------------------------------------------------------
class Error(Exception):
    """
    Local base exception.
    """


class ArgumentError(Error):
    """
    Invalid argument.
    """


class UnknownMethodError(Error):
    """
    The requested method is not supported.
    """


# -----------------------------------------------------------------------------
class Settings:
    """A dataclass for the Akeyaa analysis settings.

    Attributes
    ----------
    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey"s coding system. If None, then all
        aquifers present will be included. The default is DEFAULT_AQUIFERS.

    method : str, optional
        The fitting method. This must be one of {"OLS", "RLM"}, where
            -- "OLS" ordinary least squares regression.
            -- "RLM" robust linear model regression with Tukey biweights.
        The default is DEFAULT_METHOD.

    radius : float, optional
        Search radius for neighboring wells. radius >= 1. The default is
        DEFAULT_RADIUS.

    required : int, optional
        Required number of neighboring wells. If fewer are found, the
        target location is skipped. required >= 6. The default is
        DEFAULT_REQUIRED.

    spacing : float, optional
        Grid spacing for target locations across the county. spacing >= 1.
        The default is DEFAULT_SPACING.

    Raises
    ------
    ValueError
    """

    def __init__(self,
                 aquifers = DEFAULT_AQUIFERS,
                 method = DEFAULT_METHOD,
                 radius = DEFAULT_RADIUS,
                 required = DEFAULT_REQUIRED,
                 spacing = DEFAULT_SPACING):
        self.aquifers = aquifers
        self.method = method
        self.radius = radius
        self.required = required
        self.spacing = spacing

    def __repr__(self):
        return ("Settings("
            "aquifers={0.aquifers!r}, "
            "method={0.method!r}, "
            "radius={0.radius!r}, "
            "required={0.required!r}, "
            "spacing={0.spacing!r})".format(self))

    def __eq__(self, other):
        return ((self.__class__ == other.__class__) and
                (self.aquifers == other.aquifers) and
                (self.method == other.method) and
                (self.radius == other.radius) and
                (self.required == other.required) and
                (self.spacing == other.spacing))

    @property
    def aquifers(self):
        return self._aquifers

    @aquifers.setter
    def aquifers(self, aquifers):
        if (aquifers is not None) and (not set.issubset(set(aquifers), ALL_AQUIFERS)):
            raise ValueError("Unknown aquifer code(s)")
        else:
            self._aquifers = aquifers

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, method):
        if method not in ["OLS", "RLM"]:
            raise ValueError("'method' must be one of {'OLS', 'RLM'}")
        else:
            self._method = method

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, radius):
        if radius < 1.0:
            raise ValueError("'radius' must be >= 1")
        else:
            self._radius = radius

    @property
    def required(self):
        return self._required

    @required.setter
    def required(self, required):
        if required < 6:
            raise ValueError("'required' must be >= 6")
        else:
            self._required = required

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, spacing):
        if spacing < 1.0:
            raise ValueError("'spacing' must be >= 1")
        else:
            self._spacing = spacing


# -----------------------------------------------------------------------------
def by_venue(venue, settings):
    """Compute the Akeyaa analysis across the specified venue.

    The Akeyaa analysis is carried out at target locations within the
    <venue>"s polygon. The target locations are selected as the nodes of a
    square grid covering the venue"s polygon.

    The square grid of target locations is anchored at the centroid of the
    <venue>"s polygon, and the grid lines are separated by <spacing>.
    If a target location is not inside of the venue"s polygon it is discarded.

    For each remaining target location all wells in the <database> that
    satisfy the following two conditions are identified:
        (1) completed in one or more of the <aquifers>, and
        (2) within a horizontal distance of <radius> of the target location.
    If a target location has fewer than <required> identified (neighboring)
    wells it is discarded.

    The Akeyaa analysis is carried out at each of the remaining target
    locations using the <method> for fitting the conic potential model.

    Parameters
    ----------
    venue: venues.Venue (concrete subclass)
        An instance of a concrete subclass of venues.Venue, e.g. City.

    settings : settings.Settings
        A complete set of akeyaa settings.

        aquifers : list, optional
            List of four-character aquifer abbreviation strings, as defined in
            Minnesota Geologic Survey"s coding system. If None, then all
            aquifers present will be included. The default is DEFAULT_AQUIFERS.

        method : str, optional
            The fitting method. This must be one of {"OLS", "RLM"}, where
                -- "OLS" ordinary least squares regression.
                -- "RLM" robust linear model regression with Tukey biweights.
            The default is DEFAULT_METHOD.

        radius : float, optional
            Search radius for neighboring wells. radius >= 1. The default is
            DEFAULT_RADIUS.

        required : int, optional
            Required number of neighboring wells. If fewer are found, the
            target location is skipped. required >= 6. The default is
            DEFAULT_REQUIRED.

        spacing : float, optional
            Grid spacing for target locations across the county. spacing >= 1.
            The default is DEFAULT_SPACING.

    Returns
    -------
    results : list of tuples
        (xtarget, ytarget, n, evp, varp)
        -- xtarget : float
               x-coordinate of target location.
        -- ytarget : float
               y-coordinate of target location.
        -- n : int
               number of neighborhood wells used in the local analysis.
        -- evp : ndarray, shape=(6,1)
               expected value vector of the prarameters.
        -- varp : ndarray, shape=(6,6)
               variance/covariance matrix of the settings.

    Notes
    -----
    o   Note, data from outside of the venue may also used in the
        computations. However, only data from the Minnesota CWI are
        considered.
    """
    return by_polygon(venue.polygon, settings)


# -----------------------------------------------------------------------------
def by_polygon(polygon, settings):
    """Compute the Akeyaa analysis across the specified polygon.

    The Akeyaa analysis is carried out at discrete target locations within
    the <polygon>. The target locations are selected as the nodes of a square
    grid covering the <polygon>.

    The square grid of target locations is anchored at the centroid of the
    <polygon>, axes aligned, and the grid lines are separated by <spacing>.
    The extent of the grid captures all of the vertices of the polygon.
    If a target location is not inside of the <polygon> it is discarded.

    For each remaining target location all wells in the <database> that
    satisfy the following two conditions are identified:
        (1) completed in one or more of the <aquifers>, and
        (2) within a horizontal distance of <radius> of the target location.
    If a target location has fewer than <required> identified (neighboring)
    wells it is discarded.

    The Akeyaa analysis is carried out at each of the remaining target
    locations using the <method> for fitting the conic potential model.

    Parameters
    ----------
    polygon : geometry.Polygon

    settings : settings.Settings
        aquifers : list, optional
            List of four-character aquifer abbreviation strings, as defined in
            Minnesota Geologic Survey"s coding system. If None, then all
            aquifers present will be included. The default is DEFAULT_AQUIFERS.

        method : str, optional
            The fitting method. This must be one of {"OLS", "RLM"}, where
                -- "OLS" ordinary least squares regression.
                -- "RLM" robust linear model regression with Tukey biweights.
            The default is DEFAULT_METHOD.

        radius : float, optional
            Search radius for neighboring wells. radius >= 1. The default is
            DEFAULT_RADIUS.

        required : int, optional
            Required number of neighboring wells. If fewer are found, the
            target location is skipped. required >= 6. The default is
            DEFAULT_REQUIRED.

        spacing : float, optional
            Grid spacing for target locations across the venue. spacing >= 1.
            The default is DEFAULT_SPACING.

    Returns
    -------
    results : list of tuples
        (xtarget, ytarget, n, evp, varp)
        -- xtarget : float
               x-coordinate of target location.
        -- ytarget : float
               y-coordinate of target location.
        -- n : int
               number of neighborhood wells used in the local analysis.
        -- evp : ndarray, shape=(6,1)
               expected value vector of the prarameters.
        -- varp : ndarray, shape=(6,6)
               variance/covariance matrix of the settings.

    Notes
    -----
    o   Note, data from outside of the <polygon> may also used in the
        computations. However, only data from the Minnesota CWI are
        considered.
    """

    database = wells.Database()
    xgrd, ygrd = layout_the_grid(polygon, settings.spacing)

    results = []
    for xo in xgrd:
        for yo in ygrd:
            if polygon.contains((xo, yo)):
                xw, yw, zw = database.fetch(xo, yo, settings.radius, settings.aquifers)

                # Note that we are converting the zw from [ft] to [m].
                if len(xw) >= settings.required:
                    evp, varp = fit_conic_potential(xw-xo, yw-yo, 0.3048*zw, settings.method)
                    results.append((xo, yo, len(xw), evp, varp))

    return results


# -----------------------------------------------------------------------------
def layout_the_grid(polygon, spacing):
    """Determine the locations of the x and y grid lines.

    The square grid of target locations is anchored at the centroid of the
    <polygon>, axes aligned, and the grid lines are separated by <spacing>.
    The extent of the grid captures all of the vertices of the polygon.

    Parameters
    ----------
    polygon : geometry.Polygon

    spacing : float, optional
        Grid spacing for target locations across the venue.

    Returns
    -------
    xgrd : list of floats
        x-coordinates of the vertical gridlines.

    ygrd : list of floats
        y-coordinates of the horizontal gridlines.

    """

    xgrd = [polygon.centroid()[0]]
    while xgrd[-1] > polygon.extent()[0]:
        xgrd.append(xgrd[-1] - spacing)
    xgrd.reverse()
    while xgrd[-1] < polygon.extent()[1]:
        xgrd.append(xgrd[-1] + spacing)

    ygrd = [polygon.centroid()[1]]
    while ygrd[-1] > polygon.extent()[2]:
        ygrd.append(ygrd[-1] - spacing)
    ygrd.reverse()
    while ygrd[-1] < polygon.extent()[3]:
        ygrd.append(ygrd[-1] + spacing)

    return (xgrd, ygrd)


# -----------------------------------------------------------------------------
def fit_conic_potential(x, y, z, method):
    """Fit the local conic potential model to the selected heads.

    Parameters
    ----------
    x : ndarray, shape=(N,)
        x-coordinates of observation locations [m].

    y : ndarray, shape=(N,)
        y-coordinates of observation locations [m].

    z : ndarray, shape=(N,)
        observed head values [m].

    method : str
        The fitting method; one of {"OLS", "RLM"}, where
        -- "OLS" ordinary least squares regression.
        -- "RLM" robust linear model regression with Tukey biweights.

    Returns
    -------
    evp : ndarray, shape=(6,)
        The expected value vector for the model settings.

    varp : ndarray, shape=(6, 6)
        The variance matrix for the model settings.

    Raises
    ------
    None.

    Notes
    -----
    o   The underlying conic discharge potential model is

            z = A*x**2 + B*y**2 + C*x*y + D*x + E*y + F + noise

        where the settings map as: [A, B, C, D, E, F] = p[0:5].

    o   Note that most of the work is done by the statsmodels library. There
        are other fitting methods available.
    """

    X = np.stack([x**2, y**2, x*y, x, y, np.ones(x.shape)], axis=1)

    if method == "OLS":
        ols_model = sm.OLS(z, X)
        ols_results = ols_model.fit()

        evp = ols_results.params
        varp = ols_results.cov_params()

    elif method == "RLM":
        rlm_model = sm.RLM(z, X, M=sm.robust.norms.TukeyBiweight())
        rlm_results = rlm_model.fit()

        evp = rlm_results.params
        varp = rlm_results.bcov_scaled

    else:
        raise UnknownMethodError

    return (evp, varp)
