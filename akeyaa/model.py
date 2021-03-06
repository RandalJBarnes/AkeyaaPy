"""Implement the Model class in the MVC pattern for AkeyaaPy.

This modules contains the working functions that perform the Akeyaa analysis
across a venue.

Notes
-----
*Akeyaa analysis* entails the fitting of the  conic potential model at
many target locations within the `venue`. The target locations are selected
as the nodes of a square grid covering the `venue`. The square grid of
target locations is anchored at the centroid of the `venue`'s domain,
and the grid lines are separated by `spacing`.

If a target location is not inside of the `venue` it is discarded. For each
remaining target location, all wells that satisfy the following criteria
are identified:

- the well is within a horizontal distance of `radius` of the target location,
- the well is completed in one or more of the `aquifers`,
- the water level measurement date is on or after `after`, and
- the water level measurement date is on or before `before`.

If a target location has fewer than `required` identified (neighboring)
wells it is discarded. The Akeyaa analysis is carried out at each of the
remaining target locations using the `method` for fitting the conic
potential model.

Data from outside of the venue may be used in the computations.

"""
from itertools import compress
import numpy as np
import statsmodels.api as sm

__author__ = "Randal J Barnes"
__version__ = "24 August 2020"


def model_by_venue(wells, venue, aquifers, parameters):
    """Compute the Akeyaa analysis across the specified venue.

    Arguments
    ---------
    wells: Wells


    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `akeyaa.venues`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    aquifers : list[str]
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. If None, then all
        aquifers present will be included. The default is DEFAULT_AQUIFERS.

    parameters : dictionary
        ["radius"]:
            "required": self.required.get(),
            "spacing": self.spacing.get(),
            "firstyear": self.firstyear.get(),
            "lastyear": self.lastyear.get()

        ["radius"] : float
            Search radius for neighboring wells. radius >= 1.

        ["required"] : int
            Required number of neighboring wells. If fewer are found, the
            target location is skipped. required >= 6.

        ["spacing"] : float
            Grid spacing for target locations across the county. spacing >= 1.


        ["firstyear"] : int
            Water levels measured before firstyear, YYYY, are not included.

        ["lastyear"] : int
            Water levels measured after lastyear, YYYY, are not included.

    Returns
    -------
    results : list[tuple] (xytarget, n, evp, varp)

        xytarget : tuple (float, float)
            x- and y-coordinates of target location.
        n : int
            number of naerby wells used in the local analysis.
        evp : (6, 1) ndarray
            expected value vector of the model parameters.
        varp : (6, 6) ndarray
            variance/covariance matrix of the model parameters.

    See Also
    --------
    akeyaa.wells

    """
    targets = layout_the_targets(venue, parameters["spacing"])

    results = []
    for xytarget in targets:
        welldata = wells.fetch(
            xytarget,
            parameters["radius"],
            aquifers,
            parameters["firstyear"],
            parameters["lastyear"]
        )
        if len(welldata) >= parameters["required"]:
            xyz = [row[0:2] for row in welldata]
            evp, varp = fit_conic_potential(xytarget, xyz)
            results.append((xytarget, len(xyz), evp, varp))

    return results


def layout_the_targets(venue, spacing):
    """Determine the evenly-spaced locations of the x and y grid lines.

    The grid lines of target locations are anchored at the centroid of the
    `venue`, axes-aligned, and the separated by `spacing`. The outer extent
    of the grid captures all of the vertices of the `venue`.

    The grid nodes are then filtered so that only nodes inside of the venue
    are retained.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `akeyaa.venues`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    spacing : float
        Grid spacing for target locations across the venue. The grid is
        square, so only one `spacing` is needed.

    Returns
    -------
    targets : list[tuple] (xtarget, ytarget)
        x- and y-coordinates of the target points.

    See Also
    --------
    akeyaa.venues

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

    xygrd = []
    for x in xgrd:
        for y in ygrd:
            xygrd.append((x, y))
    flag = venue.contains_points(xygrd)
    return list(compress(xygrd, flag))


def fit_conic_potential(xytarget, xyz):
    """Fit the local conic potential model to the selected heads.

    Parameters
    ----------
    xytarget : tuple (xtarget, ytarget)
        The x- and y-coordinates in "NAD 83 UTM 15N" (EPSG:26915) [m] of
        the target location.

    xyz : list[tuple]
        each tuple is of the form ((x, y), z), where

        (x, y) : tuple(float, float)
            The x- and y-coordinates in "NAD 83 UTM 15N" (EPSG:26915) [m].
        z : float
            The recorded static water level [ft]

    Returns
    -------
    evp : (6,) ndarray
        The expected value vector for the fitted model parameters.

    varp : (6, 6) ndarray
        The variance/covariance matrix for the fitted model parameters.

    See Also
    --------
    statsmodels.RLM

    Notes
    -----
    The underlying conic potential model is

        z = Ax^2 + By^2 + Cxy + Dx + Ey + F + noise

    where the fitted parameters map as: [A, B, C, D, E, F] = p[0:5].

    """
    x = np.array([row[0][0] for row in xyz], dtype=float) - xytarget[0]
    y = np.array([row[0][1] for row in xyz], dtype=float) - xytarget[1]
    z = np.array([row[1] for row in xyz], dtype=float) * 0.3048                 # [ft] to [m].

    exog = np.stack([x**2, y**2, x*y, x, y, np.ones(x.shape)], axis=1)

    method_norm = sm.robust.norms.TukeyBiweight()
    rlm_model = sm.RLM(z, exog, method_norm)
    rlm_results = rlm_model.fit()
    evp = rlm_results.params
    varp = rlm_results.bcov_scaled

    return (evp, varp)
