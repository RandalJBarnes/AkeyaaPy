"""Akeyaa visualization tools.

by_venue(venue, results)
    Driver to plot the results.

local_flow_direction(venue, results)
    Plot the local flow directions.

local_number_of_wells(venue, results)
    Plot the local number of wells.

local_head(venue, results)
    Plot the magnitude of the local head.

local_gradient(venue, results)
    Plot the local head gradient.

local_gradient_quantile(venue, results)
    Plot the relative magnitude of the local head gradient.

local_laplacian_zscore(venue, results)
    Plot the local laplacian z-score.

"""
import math

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np

import pnorm


# -----------------------------------------------------------------------------
class Error(Exception):
    """The base exception for the module."""


class NotFoundError(Error):
    """Requested item was not found."""


class ArgumentError(Error):
    """Invalid argument."""


class EmptySelectionError(Error):
    """There are no wells in the selection."""


# -----------------------------------------------------------------------------
def by_venue(venue, results):
    """Driver to plot the results for the venue.

    Make five plots that highlight the results of the run.

    - The number of wells used in each local model fit.
    - The local vertically-averaged head.
    - The local vertically-averaged flow direction.
    - The magnitude of the gradient of the local vertically-averaged head.
    - The laplacian zscore.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `venues.py`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    results : list[tuples] (xtarget, ytarget, n, evp, varp)

        - xtarget : float
            x-coordinate of target location.
        - ytarget : float
            y-coordinate of target location.
        - n : int
            number of neighborhood wells used in the local analysis.
        - evp : ndarray, shape=(6,1)
            expected value vector of the prarameters.
        - varp : ndarray, shape=(6,6)
            variance/covariance matrix of the parameters.

    Returns
    -------
    None

    """
    local_number_of_wells(venue, results)
    local_head(venue, results)
    local_flow_direction(venue, results)
    local_gradient(venue, results)
    local_laplacian_zscore(venue, results)

    plt.draw_all()


# -----------------------------------------------------------------------------
def local_number_of_wells(venue, results):
    """Plot the local number of wells.

    Plot the grid showing the number of local wells used in the analysis as
    color-coded markers.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `venues.py`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    results : list[tuples] (xtarget, ytarget, n, evp, varp)

        - xtarget : float
            x-coordinate of target location.
        - ytarget : float
            y-coordinate of target location.
        - n : int
            number of neighborhood wells used in the local analysis.
        - evp : ndarray, shape=(6,1)
            expected value vector of the prarameters.
        - varp : ndarray, shape=(6,6)
            variance/covariance matrix of the parameters.

    Returns
    -------
    None

    """
    bdry = venue.boundary()

    xtarget = np.array([row[0] for row in results])
    ytarget = np.array([row[1] for row in results])
    ntarget = np.array([row[2] for row in results], dtype=int)

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    plt.scatter(xtarget, ytarget, c=ntarget, zorder=10, cmap="PuBu")
    cbar = plt.colorbar()
    cbar.ax.set_title("Count [#]")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Number of Local Wells", {"fontsize": 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def local_head(venue, results):
    """Plot the magnitude of the local head.

    Plot the grid showing the relative magnitude of the estimated local head
    as color-coded markers.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `venues.py`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    results : list[tuples] (xtarget, ytarget, n, evp, varp)

        - xtarget : float
            x-coordinate of target location.
        - ytarget : float
            y-coordinate of target location.
        - n : int
            number of neighborhood wells used in the local analysis.
        - evp : ndarray, shape=(6,1)
            expected value vector of the prarameters.
        - varp : ndarray, shape=(6,6)
            variance/covariance matrix of the parameters.

    Returns
    -------
    None

    """
    bdry = venue.boundary()
    xtarget = np.array([row[0] for row in results])
    ytarget = np.array([row[1] for row in results])

    head = np.empty(xtarget.shape)
    for i, row in enumerate(results):
        evp = row[3]
        head[i] = 3.28084 * evp[5]          # convert [m] to [ft].

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    plt.scatter(xtarget, ytarget, c=head, zorder=10, cmap="cool")
    cbar = plt.colorbar()
    cbar.ax.set_title("head [ft]")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local Vertically-averaged Head", {"fontsize": 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def local_flow_direction(venue, results):
    """Plot the local flow directions.

    Plot the grid of the estimated local flow directions as color-coded arrows.
    The arrow color depicts the probability that the flow direction is within
    +/- 10 degrees of the drawn arrow.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `venues.py`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    results : list[tuples] (xtarget, ytarget, n, evp, varp)

        - xtarget : float
            x-coordinate of target location.
        - ytarget : float
            y-coordinate of target location.
        - n : int
            number of neighborhood wells used in the local analysis.
        - evp : ndarray, shape=(6,1)
            expected value vector of the prarameters.
        - varp : ndarray, shape=(6,6)
            variance/covariance matrix of the parameters.

    Returns
    -------
    None

    """
    bdry = venue.boundary()
    xgrd = np.array([row[0] for row in results])
    ygrd = np.array([row[1] for row in results])

    xvec = np.empty(xgrd.shape)
    yvec = np.empty(xgrd.shape)

    p10 = np.empty(xgrd.shape)

    for i, row in enumerate(results):
        evp = row[3]
        varp = row[4]

        mu = evp[3:5]
        sigma = varp[3:5, 3:5]

        xvec[i] = -mu[0] / np.hypot(mu[0], mu[1])
        yvec[i] = -mu[1] / np.hypot(mu[0], mu[1])

        theta = math.atan2(mu[1], mu[0])
        lowerbound = theta - np.pi / 18.0
        upperbound = theta + np.pi / 18.0

        try:
            p10[i] = pnorm.pnormcdf(lowerbound, upperbound, mu, sigma)
        except OverflowError:
            p10[i] = 1.0
        except:
            raise

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    plt.quiver(xgrd, ygrd, xvec, yvec, p10, width=0.0018, zorder=10, cmap="Greens")
    cbar = plt.colorbar()
    cbar.ax.set_title("p10")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local Flow Directions", {"fontsize": 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def local_gradient(venue, results):
    """Plot the local head gradient.

    Plot the grid showing the magnitude of the estimated local head
    gradient as color-coded markers.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `venues.py`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    results : list[tuples] (xtarget, ytarget, n, evp, varp)

        - xtarget : float
            x-coordinate of target location.
        - ytarget : float
            y-coordinate of target location.
        - n : int
            number of neighborhood wells used in the local analysis.
        - evp : ndarray, shape=(6,1)
            expected value vector of the prarameters.
        - varp : ndarray, shape=(6,6)
            variance/covariance matrix of the parameters.

    Returns
    -------
    None

    """
    bdry = venue.boundary()
    xtarget = np.array([row[0] for row in results])
    ytarget = np.array([row[1] for row in results])

    magnitude = np.empty(xtarget.shape)
    for i, row in enumerate(results):
        evp = row[3]
        mu = evp[3:5]
        magnitude[i] = np.hypot(mu[0], mu[1])

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    plt.scatter(xtarget, ytarget, c=magnitude, vmin=0, zorder=10, cmap="Reds")
    cbar = plt.colorbar()
    cbar.ax.set_title("gradient")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local Vertically-averaged Gradient", {"fontsize": 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def local_laplacian_zscore(venue, results):
    """Plot the local laplacian zscore.

    Plot the grid showing the z-score for the local laplacian of the
    vertically-averaged head as color-coded markers. The colors are determined
    by the z-score and not the quantitative magnitude. However, the colormap
    places 0 in the middle. Thus, blue values (negative) indicate local net
    infiltration, red values (positive) indicate local net exfiltration.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in `venues.py`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    results : list[tuples] (xtarget, ytarget, n, evp, varp)

        - xtarget : float
            x-coordinate of target location.
        - ytarget : float
            y-coordinate of target location.
        - n : int
            number of neighborhood wells used in the local analysis.
        - evp : ndarray, shape=(6,1)
            expected value vector of the prarameters.
        - varp : ndarray, shape=(6,6)
            variance/covariance matrix of the parameters.

    Returns
    -------
    None

    """
    bdry = venue.boundary()
    xtarget = np.array([row[0] for row in results])
    ytarget = np.array([row[1] for row in results])

    score = np.empty(xtarget.shape)
    for i, row in enumerate(results):
        evp = row[3]
        varp = row[4]
        laplacian = 2*(evp[0]+evp[1])
        stdev = 2*np.sqrt(varp[0, 0] + varp[1, 1] + 2*varp[0, 1])
        score[i] = min(max(laplacian/stdev, -3), 3)

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    divnorm = colors.DivergingNorm(vmin=-3, vcenter=0, vmax=3)
    plt.scatter(xtarget, ytarget, c=score, norm=divnorm, zorder=10, cmap="bwr")
    cbar = plt.colorbar()
    cbar.ax.set_title("z-score")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local vertically-averaged Laplacian Z-score", {"fontsize": 24})
    plt.grid(True)
