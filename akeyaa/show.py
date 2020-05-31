"""Akeyaa visualization tools.

Functions
---------
results_by_venue(prefix, polygon, results    Plot the results.

local_flow_direction(prefix, polygon, results)
    Plot the local flow directions.

local_number_of_wells(prefix, polygon, results)
    Plot the local number of wells.

local_head_gradient_magnitude(prefix, polygon, results)
    Plot the relative magnitude of the local head gradient.

aquifers_by_venue(venue, aquifers)
    Plot the wells in the vnue coded by aquifer.

whereis(venue)
    Plots the venue"s polygon over the state's ploygon.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
31 May 2020
"""

import math

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import pnorm
import venues
import wells


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

    xbdry = [pnt.X for pnt in venue.polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in venue.polygon.getPart(0)]

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
        p10[i] = pnorm.pnormcdf(lowerbound, upperbound, mu, sigma)

    fig, ax1 = plt.subplots()
    plt.axis("equal")

    plt.fill(xbdry, ybdry, "0.90")
    plt.quiver(xgrd, ygrd, xvec, yvec, p10,
               width=0.0018, zorder=10, cmap="Greys")
    cbar = plt.colorbar()
    cbar.ax.set_title("p10")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname + "Local Flow Directions", {"fontsize": 24})
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

    xbdry = [pnt.X for pnt in venue.polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in venue.polygon.getPart(0)]

    xtarget = np.array([row[0] for row in results])
    ytarget = np.array([row[1] for row in results])
    ntarget = np.array([row[2] for row in results], dtype=int)

    plt.figure()
    plt.axis("equal")

    plt.fill(xbdry, ybdry, "0.90")
    plt.scatter(xtarget, ytarget, c=ntarget, zorder=10, cmap="GnBu")
    cbar = plt.colorbar()
    cbar.ax.set_title("Count [#]")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname + "Number of Local Wells", {"fontsize": 24})
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

    xbdry = [pnt.X for pnt in venue.polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in venue.polygon.getPart(0)]

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

    plt.fill(xbdry, ybdry, "0.90")
    plt.scatter(xtarget, ytarget, c=quantile, zorder=10, cmap="OrRd")
    cbar = plt.colorbar()
    cbar.ax.set_title("Quantile")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname + "|Head Gradient|", {"fontsize": 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def aquifers_by_venue(venue, aquifers=None):
    """Plot the wells in the venue coded by aquifer.

    Plot the locations of the authorized wells in the venue that are completed
    in one of the identified aquifers. The plotted marker for a well is
    color-coded by the aquifer in which it is completed.

    Parameters
    ----------
    venue : a concrete subclass of venues.Venue (i.e. City)

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

    Returns
    -------
    aquifer_info : list of tuples
        (aquifer_abbr, count)
        -- aquifer_abbr : str
                The four-character aquifer abbreviation string.
        -- count : int
                The number of wells in the associated aquifer type.
        The list is sorted in descending order by count.
    """

    xbdry = [pnt.X for pnt in venue.polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in venue.polygon.getPart(0)]

    welldata = wells.get_welldata_by_polygon(venue.polygon)

    if aquifers is None:
        xsel = [row[0] for row in welldata]
        ysel = [row[1] for row in welldata]
        asel = [row[3] for row in welldata]
    else:
        xsel = [row[0] for row in welldata if row[3] in aquifers]
        ysel = [row[1] for row in welldata if row[3] in aquifers]
        asel = [row[3] for row in welldata if row[3] in aquifers]

    if len(xsel) == 0:
        raise EmptySelectionError

    uaq, naq = np.unique(asel, return_counts=True)

    plt.figure()
    plt.axis("equal")

    plt.fill(xbdry, ybdry, "0.90")
    sns.scatterplot(xsel, ysel, hue=asel, hue_order=uaq.tolist(), zorder=10)

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname + "Wells Coded By Aquifer", {"fontsize": 24})

    aquifer_info = list(zip(uaq, naq))
    aquifer_info.sort(key=lambda tup: tup[1], reverse=True)
    return aquifer_info

# -----------------------------------------------------------------------------
def whereis(venue):
    """Plot the venue's polygon over the state's ploygon.

    Arguments
    ---------
    venue : a concrete subclass of venues.Venue (i.e. City)

    Returns
    -------
    None
    """

    xbdry = [pnt.X for pnt in venue.polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in venue.polygon.getPart(0)]

    state = venues.State(0)
    xstate = [pnt.X for pnt in state.polygon.getPart(0)]
    ystate = [pnt.Y for pnt in state.polygon.getPart(0)]

    plt.figure()
    plt.axis("equal")

    plt.fill(xstate, ystate, "0.90")
    plt.fill(xbdry, ybdry, "b")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname, {"fontsize": 24})
    plt.grid(True)
