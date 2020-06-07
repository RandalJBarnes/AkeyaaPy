"""Perform the Akeyaa analysis.

This modules contains the working function that perform the Akeyaa analysis
across a venue.

Functions
---------
by_venue(venue, settings)
    Compute the Akeyaa analysis across the specified `venue`.

layout_the_grid(venue, spacing)
    Determine the locations of the x and y grid lines to cover the `venue`.

fit_conic(x, y, z, method)
    Fit the local conic potential model to the selected measurements.

"""
import numpy as np
import statsmodels.api as sm

import wells


# -----------------------------------------------------------------------------
class Error(Exception):
    """Local base exception."""


class UnknownMethodError(Error):
    """The requested fitting method is not supported."""


# -----------------------------------------------------------------------------
def by_venue(venue, settings):
    """Compute the Akeyaa analysis across the specified venue.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `venues.py`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    settings : type
        A complete, validated set of akeyaa parameters, as enumerated and
        detailed in parameters.py.

    Returns
    -------
    results : list[tuples]
        Each tuple takes the form (xtarget, ytarget, n, evp, varp).

        xtarget : float
            x-coordinate of target location.
        ytarget : float
            y-coordinate of target location.
        n : int
            number of neighborhood wells used in the local analysis.
        evp : ndarray, shape=(6,1)
            expected value vector of the model parameters.
        varp : ndarray, shape=(6,6)
            variance/covariance matrix of the model parameters.

    Notes
    -----
    The Akeyaa analysis is carried out at target locations within the
    `venue`. The target locations are selected as the nodes of a
    square grid covering the `venue`.

    The square grid of target locations is anchored at the centroid of the
    `venue`'s domain, and the grid lines are separated by `spacing`. If a
    target location is not inside of the venue it is discarded.

    For each remaining target location, all wells that satisfy the following
    two conditions are identified:

    - completed in one or more of the `aquifers`, and
    - within a horizontal distance of `radius` of the target location.

    If a target location has fewer than `required` identified (neighboring)
    wells it is discarded.

    The Akeyaa analysis is carried out at each of the remaining target
    locations using the `method` for fitting the conic potential model.

    Data from outside of the venue may also be used in the computations.
    However, only data from the Minnesota CWI are considered.

    """
    xgrd, ygrd = layout_the_grid(venue, settings.spacing)

    results = []
    for xtarget in xgrd:
        for ytarget in ygrd:
            if venue.contains((xtarget, ytarget)):
                xwell, ywell, zwell = wells.fetch(
                    xtarget, ytarget, settings.radius, settings.aquifers
                )
                neighbors = len(xwell)

                # Note that we are converting the zw from [ft] to [m].
                if neighbors >= settings.required:
                    evp, varp = fit_conic_potential(
                        xwell - xtarget,
                        ywell - ytarget,
                        0.3048 * zwell,
                        settings.method,
                    )
                    results.append((xtarget, ytarget, neighbors, evp, varp))

    return results


# -----------------------------------------------------------------------------
def layout_the_grid(venue, spacing):
    """Determine the locations of the x and y grid lines.

    The square grid of target locations is anchored at the centroid of the
    `venue`, axes aligned, and the grid lines are separated by `spacing`.
    The extent of the grid captures all of the vertices of the domain.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in venues.py.
        For example: a 'City', 'Watershed', or 'Neighborhood'.

    spacing : float
        Grid spacing for target locations across the venue. The grid is
        square, so only one `spacing` is needed.

    Returns
    -------
    xgrd : list[float]
        x-coordinates of the vertical gridlines.

    ygrd : list[float]
        y-coordinates of the horizontal gridlines.

    """
    xgrd = [venue.centroid()[0]]
    while xgrd[-1] > venue.extent()[0]:
        xgrd.append(xgrd[-1] - spacing)
    xgrd.reverse()
    while xgrd[-1] < venue.extent()[1]:
        xgrd.append(xgrd[-1] + spacing)

    ygrd = [venue.centroid()[1]]
    while ygrd[-1] > venue.extent()[2]:
        ygrd.append(ygrd[-1] - spacing)
    ygrd.reverse()
    while ygrd[-1] < venue.extent()[3]:
        ygrd.append(ygrd[-1] + spacing)

    return (xgrd, ygrd)


# -----------------------------------------------------------------------------
def fit_conic_potential(x, y, z, method):
    """Fit the local conic potential model to the selected heads.

    Parameters
    ----------
    x : ndarray, shape=(n,)
        x-coordinates of observation locations [m].

    y : ndarray, shape=(n,)
        y-coordinates of observation locations [m].

    z : ndarray, shape=(n,)
        observed head values [m].

    method : str
        The fitting method; one of {"OLS", "TUKEY", "HUBER"}.

        - "OLS" ordinary least squares regression.
        - "TUKEY" robust linear model regression with Tukey biweights.
        - "HUBER" robust linear model regression with Huber T weights.

    Returns
    -------
    evp : ndarray, shape=(6,)
        The expected value vector for the fitted model parameters.

    varp : ndarray, shape=(6, 6)
        The variance/covariance matrix for the fitted model parameters.

    Notes
    -----
    The underlying conic discharge potential model is

        z = Ax^2 + By^2 + Cxy + Dx + Ey + F + noise

    where the fitted parameters map as: [A, B, C, D, E, F] = p[0:5].

    """
    X = np.stack([x**2, y**2, x*y, x, y, np.ones(x.shape)], axis=1)

    if method == "OLS":
        ols_model = sm.OLS(z, X)
        ols_results = ols_model.fit()

        evp = ols_results.params
        varp = ols_results.cov_params()

    elif method == "TUKEY":
        rlm_model = sm.RLM(z, X, M=sm.robust.norms.TukeyBiweight())
        rlm_results = rlm_model.fit()

        evp = rlm_results.params
        varp = rlm_results.bcov_scaled

    elif method == "HUBER":
        rlm_model = sm.RLM(z, X, M=sm.robust.norms.HuberT())
        rlm_results = rlm_model.fit()

        evp = rlm_results.params
        varp = rlm_results.bcov_scaled

    else:
        raise UnknownMethodError

    return (evp, varp)
