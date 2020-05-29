"""
Akeyaa visualization tools.

Functions
---------

----- groundwater -----
load_and_show_results(pklzfile)
    Load the run from a .pklz file and plot the results.

show_results(prefix, polygon, results)
    Plot the results.

show_local_flow_direction(prefix, polygon, results)
    Plot the local flow directions.

show_local_number_of_wells(prefix, polygon, results)
    Plot the local number of wells.

show_local_head_gradient_magnitude(prefix, polygon, results)
    Plot the relative magnitude of the local head gradient.

----- geography -----
whereis(obj)
    Plots the objects polygon over the state.

show_polygon_in_state(polygon, title_str=None)
    Plot the polygon in the state.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
28 May 2020

"""

import bz2
import pickle
import math

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import pnorm
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






# -----------------------------------------------------------------------------
def load_and_show_results(pklzfile):
    """
    Load the run from a .pklz file and plot the results.

    Parameters
    ----------
    pklzfile : str
        Compressed pickle file path/name for the run.

    Returns
    -------
    None
    """

    # Get the run data from the pickle file.
    with bz2.open(pklzfile, 'rb') as fileobject:
        archive = pickle.load(fileobject)

    prefix = archive.get('prefix')
    polygon = archive.get('polygon')
    results = archive.get('results')

    show_results(prefix, polygon, results)


# -----------------------------------------------------------------------------
def show_results(prefix, polygon, results):
    """
    Plot the results.

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
    prefix : str
        The project-specifc (but not plot-specific) part of each plot title.

    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the run.

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

    show_local_flow_direction(prefix, polygon, results)
    show_local_number_of_wells(prefix, polygon, results)
    show_local_head_gradient_magnitude(prefix, polygon, results)

    plt.draw_all()


# -----------------------------------------------------------------------------
def show_local_flow_direction(prefix, polygon, results):
    """
    Plot the local flow directions.

    Plot the grid of the estimated local flow directions as color-coded arrows.
    The arrow color depicts the probability that the flow direction is within
    +/- 10 degrees of the drawn arrow.

    Parameters
    ----------
    prefix : str
        The project-specifc (but not plot-specific) part of each plot title.

    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the run.

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

    # Get the polygon boundary information.
    xbdry = [pnt.X for pnt in polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in polygon.getPart(0)]

    # Extract and collate the run information.
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
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    plt.quiver(xgrd, ygrd, xvec, yvec, p10,
               width=0.0018, zorder=10, cmap='Greys')
    cbar = plt.colorbar()
    cbar.ax.set_title('p10')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title(prefix + 'Local Flow Directions', {'fontsize': 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def show_local_number_of_wells(prefix, polygon, results):
    """
    Plot the local number of wells.

    Plot the grid showing the number of local wells used in the analysis as
    color-coded markers.

    Parameters
    ----------
    prefix : str
        The project-specifc (but not plot-specific) part of each plot title.

    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the run.

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

    # Get the polygon boundary information.
    xbdry = [pnt.X for pnt in polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in polygon.getPart(0)]

    # Extract and collate the run information.
    xgrd = np.array([row[0] for row in results])
    ygrd = np.array([row[1] for row in results])
    ngrd = np.array([row[2] for row in results], dtype=int)

    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    plt.scatter(xgrd, ygrd, c=ngrd, zorder=10, cmap='GnBu')
    cbar = plt.colorbar()
    cbar.ax.set_title('Count [#]')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title(prefix + 'Number of Local Wells', {'fontsize': 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def show_local_head_gradient_magnitude(prefix, polygon, results):
    """
    Plot the relative magnitude of the local head gradient.

    Plot the grid showing the relative magnitude of the estimated local head
    gradient as color-coded markers. The colors are determined by the quantile
    and not the quantitative magnitude.

    Parameters
    ----------
    prefix : str
        The project-specifc (but not plot-specific) part of each plot title.

    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the run.

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

    # Get the polygon boundary information.
    xbdry = [pnt.X for pnt in polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in polygon.getPart(0)]

    # Extract and collate the run information.
    xgrd = np.array([row[0] for row in results])
    ygrd = np.array([row[1] for row in results])

    mag = np.empty(xgrd.shape)

    for i, row in enumerate(results):
        evp = row[3]
        mu = evp[3:5]
        mag[i] = np.hypot(mu[0], mu[1])

    jdx = np.argsort(np.argsort(mag))
    quantile = (jdx+0.5)/len(jdx)

    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    plt.scatter(xgrd, ygrd, c=quantile, zorder=10, cmap='OrRd')
    cbar = plt.colorbar()
    cbar.ax.set_title('Quantile')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title(prefix + '|Head Gradient|', {'fontsize': 24})
    plt.grid(True)


# -----------------------------------------------------------------------------
def show_aquifers(prefix, polygon, aquifers=None):
    """
    Plot the wells in the vnue coded by aquifer.

    Plot the locations of the authorized wells in the venue that are completed
    in one of the identified aquifers. The plotted marker for a well is
    color-coded by the aquifer in which it is completed.

    Parameters
    ----------
    venue : Venue

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

    # Get the polygon boundary information.
    xbdry = [pnt.X for pnt in polygon.getPart(0)]
    ybdry = [pnt.Y for pnt in polygon.getPart(0)]

    # Get the data for wells in the polygon.
    welldata = wells.get_welldata_by_polygon(polygon, aquifers)

    xwell = [row[0][0] for row in welldata]
    ywell = [row[0][1] for row in welldata]
    awell = [row[2] for row in welldata]

    # Determine a list of unique aquifers present and their associated counts.
    uaq, naq = np.unique(awell, return_counts=True)

    aquifer_info = [(uaq[i], naq[i]) for i in range(len(uaq))]
    aquifer_info.sort(key=lambda tup: tup[1], reverse=True)

    # Plot the well locations coded by aquifer.
    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    sns.scatterplot(xwell, ywell, hue=awell, hue_order=uaq.tolist(), zorder=10)

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title(prefix + 'Wells Coded By Aquifer', {'fontsize': 24})

    return aquifer_info
