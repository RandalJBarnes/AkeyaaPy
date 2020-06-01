"""The functions to carry out the actual Akeyaa analysis.

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

import arcpy

import wells


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
    polygon : arcpy.arcobjects.geometries.Polygon
        An arcpy.Polygon with the vertex coordinates represented in
        "NAD 83 UTM zone 15N" (EPSG:26915),

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
            if polygon.contains(arcpy.Point(xo, yo)):
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
    polygon : arcpy.arcobjects.geometries.Polygon
        An arcpy.Polygon with the vertex coordinates represented in
        "NAD 83 UTM zone 15N" (EPSG:26915),

    spacing : float, optional
        Grid spacing for target locations across the venue.

    Returns
    -------
    xgrd : list of floats
        x-coordinates of the vertical gridlines.

    ygrd : list of floats
        y-coordinates of the horizontal gridlines.

    """

    xgrd = [polygon.centroid.X]
    while xgrd[-1] > polygon.extent.XMin:
        xgrd.append(xgrd[-1] - spacing)
    xgrd.reverse()
    while xgrd[-1] < polygon.extent.XMax:
        xgrd.append(xgrd[-1] + spacing)

    ygrd = [polygon.centroid.Y]
    while ygrd[-1] > polygon.extent.YMin:
        ygrd.append(ygrd[-1] - spacing)
    ygrd.reverse()
    while ygrd[-1] < polygon.extent.YMax:
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
