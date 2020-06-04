"""Akeyaa visualization tools.

Functions
---------
results_by_venue(prefix, domain, results    Plot the results.

local_flow_direction(prefix, domain, results)
    Plot the local flow directions.

local_number_of_wells(prefix, domain, results)
    Plot the local number of wells.

local_head_gradient_magnitude(prefix, domain, results)
    Plot the relative magnitude of the local head gradient.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
04 June 2020
"""

import math

import matplotlib.pyplot as plt
import numpy as np

import pnorm


# -----------------------------------------------------------------------------
class Error(Exception):
    """
    The base exception for the module.
    """


class NotFoundError(Error):
    """
    Requested item was not found.
    """


class ArgumentError(Error):
    """
    Invalid argument.
    """

class EmptySelectionError(Error):
    """
    There are no wells in the selection.
    """


# -----------------------------------------------------------------------------
def results_by_venue(venue, results):
    """Plot the results for the venue.

    Make three plots that highlight the results of the run.
    -- Plot the grid of local flow directions as color-coded arrows. The
        arrow color depicts the probability that the flow direction is
        within +/- 10 degrees of the drawn arrow.

    -- Plot the grid showing the number of local wells used in the
        analysis as color-coded markers.

    -- Plot the grid showing the relative magnitude of the local head gradient
        as color-coded markers. The colors are determined by the quantile
        and not the quantitative magnitude.

    Parameters
    ----------
    venue : a concrete subclass of venues.Venue (i.e. City)

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
               variance/covariance matrix of the parameters.

    Returns
    -------
    None
    """

    local_flow_direction(venue, results)
    local_number_of_wells(venue, results)
    local_head_gradient_magnitude(venue, results)

    plt.draw_all()


# -----------------------------------------------------------------------------
def local_flow_direction(venue, results):
    """Plot the local flow directions.

    Plot the grid of the estimated local flow directions as color-coded arrows.
    The arrow color depicts the probability that the flow direction is within
    +/- 10 degrees of the drawn arrow.

    Parameters
    ----------
    venue : a concrete subclass of venues.Venue (i.e. City)

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
               variance/covariance matrix of the parameters.

    Returns
    -------
    None
    """

    bdry = venue.domain.boundary()
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

        xvec[i] = -mu[0]/np.hypot(mu[0], mu[1])
        yvec[i] = -mu[1]/np.hypot(mu[0], mu[1])

        theta = math.atan2(mu[1], mu[0])
        lowerbound = theta - np.pi/18.0
        upperbound = theta + np.pi/18.0

        try:
            p10[i] = pnorm.pnormcdf(lowerbound, upperbound, mu, sigma)
        except OverflowError:
            p10[i] = 1.0
        except:
            raise

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.90")
    plt.quiver(xgrd, ygrd, xvec, yvec, p10,
               width=0.0018, zorder=10, cmap='Greens')
    cbar = plt.colorbar()
    cbar.ax.set_title("p10")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local Flow Directions", {"fontsize": 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def local_number_of_wells(venue, results):
    """Plot the local number of wells.

    Plot the grid showing the number of local wells used in the analysis as
    color-coded markers.

    Parameters
    ----------
    venue : a concrete subclass of venues.Venue (i.e. City)

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
               variance/covariance matrix of the parameters.

    Returns
    -------
    None
    """

    bdry = venue.domain.boundary()

    xtarget = np.array([row[0] for row in results])
    ytarget = np.array([row[1] for row in results])
    ntarget = np.array([row[2] for row in results], dtype=int)

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.90")
    plt.scatter(xtarget, ytarget, c=ntarget, zorder=10, cmap="GnBu")
    cbar = plt.colorbar()
    cbar.ax.set_title("Count [#]")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Number of Local Wells", {"fontsize": 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def local_head_gradient_magnitude(venue, results):
    """Plot the relative magnitude of the local head gradient.

    Plot the grid showing the relative magnitude of the estimated local head
    gradient as color-coded markers. The colors are determined by the quantile
    and not the quantitative magnitude.

    Parameters
    ----------
    venue : a concrete subclass of venues.Venue (i.e. City)

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
               variance/covariance matrix of the parameters.

    Returns
    -------
    None
    """

    bdry = venue.domain.boundary()
    xtarget = np.array([row[0] for row in results])
    ytarget = np.array([row[1] for row in results])

    magnitude = np.empty(xtarget.shape)
    for i, row in enumerate(results):
        evp = row[3]
        mu = evp[3:5]
        magnitude[i] = np.hypot(mu[0], mu[1])

    jdx = np.argsort(np.argsort(magnitude))
    quantile = (jdx+0.5)/len(jdx)

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.90")
    plt.scatter(xtarget, ytarget, c=quantile, zorder=10, cmap="OrRd")
    cbar = plt.colorbar()
    cbar.ax.set_title("Quantile")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " |Head Gradient|", {"fontsize": 24})
    plt.grid(True)
