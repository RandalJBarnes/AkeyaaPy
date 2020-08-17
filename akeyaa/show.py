"""Akeyaa visualization tools.

There are five separate plots that constructed from the model results by the
driver function

    * show_results_by_venue(venue, results)

These plots are

    * local_flow_direction(venue, results)
        Plot the local flow directions.

    * local_number_of_wells(venue, results)
        Plot the local number of wells.

    * local_head(venue, results)
        Plot the magnitude of the local head.

    * local_gradient(venue, results)
        Plot the local head gradient.

    * local_laplacian_zscore(venue, results)
        Plot the local laplacian z-score.

In addition, the aquifers represented in a venue are plot by

    * show_aquifers_by_venue(wells, venue, aquifers, parameters

"""
import math

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
import seaborn as sns

import akeyaa.pnorm as pnorm

__author__ = "Randal J Barnes"
__version__ = "17 August 2020"

FIGSIZE = (10, 8)               # initial figure size [in]

# -----------------------------------------------------------------------------
def show_results_by_venue(venue, results):
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

    results : list[tuples] (xytarget, n, evp, varp)

        - xytarget : tuple(float, float)
            x- and y-coordinates of target location.
        - n : int
            number of neighborhood wells used in the local analysis.
        - evp : ndarray, shape=(6,1)
            expected value vector of the prarameters.
        - varp : ndarray, shape=(6,6)
            variance/covariance matrix of the parameters.

    Returns
    -------
    target_values : dictionary

    """
    xtarget, ytarget, xvec, yvec, p10 = local_flow_direction(venue, results)
    _, _, ntarget = local_number_of_wells(venue, results)
    _, _, head = local_head(venue, results)
    _, _, magnitude = local_gradient(venue, results)
    _, _, score = local_laplacian_zscore(venue, results)

    plt.draw_all()
    plt.show(block=False)

    target_values = {
        "xtarget": xtarget,
        "ytarget": ytarget,
        "xvec": xvec,
        "yvec": yvec,
        "p10": p10,
        "ntarget": ntarget,
        "head": head,
        "magnitude": magnitude,
        "score": score
    }

    return target_values


# -----------------------------------------------------------------------------
def local_flow_direction(venue, results):
    """Plot the local flow directions.

    Plot the grid of the estimated local flow directions as color-coded arrows.
    The arrow color depicts the probability that the flow direction is within
    +/- 10 degrees of the drawn arrow.

    """
    xtarget = np.array([row[0][0] for row in results])
    ytarget = np.array([row[0][1] for row in results])

    bdry = venue.boundary()

    xvec = np.empty(xtarget.shape)
    yvec = np.empty(xtarget.shape)

    p10 = np.empty(xtarget.shape)

    for i, row in enumerate(results):
        evp = row[2]
        varp = row[3]
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

    plt.figure(figsize=FIGSIZE)
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    plt.quiver(xtarget, ytarget, xvec, yvec, p10, width=0.0018, zorder=10, cmap="Greens")
    cbar = plt.colorbar()
    cbar.ax.set_title("p10")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local Flow Directions", {"fontsize": 18})
    plt.grid(True)

    return (xtarget, ytarget, xvec, yvec, p10)


# -----------------------------------------------------------------------------
def local_number_of_wells(venue, results):
    """Plot the local number of wells.

    Plot the grid showing the number of local wells used in the analysis as
    color-coded markers.

    """
    xtarget = np.array([row[0][0] for row in results])
    ytarget = np.array([row[0][1] for row in results])
    ntarget = np.array([row[1] for row in results], dtype=int)

    bdry = venue.boundary()

    plt.figure(figsize=FIGSIZE)
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    plt.scatter(xtarget, ytarget, c=ntarget, zorder=10, cmap="PuBu")
    cbar = plt.colorbar()
    cbar.ax.set_title("Count [#]")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Number of Local Wells", {"fontsize": 18})
    plt.grid(True)

    return (xtarget, ytarget, ntarget)

# -----------------------------------------------------------------------------
def local_head(venue, results):
    """Plot the magnitude of the local head.

    Plot the grid showing the relative magnitude of the estimated local head
    as color-coded markers.

    """
    xtarget = np.array([row[0][0] for row in results])
    ytarget = np.array([row[0][1] for row in results])

    bdry = venue.boundary()

    head = np.empty(xtarget.shape)
    for i, row in enumerate(results):
        evp = row[2]
        head[i] = 3.28084 * evp[5]          # convert [m] to [ft].

    plt.figure(figsize=FIGSIZE)
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    plt.scatter(xtarget, ytarget, c=head, zorder=10, cmap="cool")
    cbar = plt.colorbar()
    cbar.ax.set_title("head [ft]")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local Vertically-averaged Head", {"fontsize": 18})
    plt.grid(True)

    return (xtarget, ytarget, head)

# -----------------------------------------------------------------------------
def local_gradient(venue, results):
    """Plot the local head gradient.

    Plot the grid showing the magnitude of the estimated local head
    gradient as color-coded markers.

    """
    xtarget = np.array([row[0][0] for row in results])
    ytarget = np.array([row[0][1] for row in results])

    bdry = venue.boundary()

    magnitude = np.empty(xtarget.shape)
    for i, row in enumerate(results):
        evp = row[2]
        mu = evp[3:5]
        magnitude[i] = np.hypot(mu[0], mu[1])

    plt.figure(figsize=FIGSIZE)
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    plt.scatter(xtarget, ytarget, c=magnitude, vmin=0, zorder=10, cmap="Reds")
    cbar = plt.colorbar()
    cbar.ax.set_title("gradient")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local Vertically-averaged Gradient", {"fontsize": 18})
    plt.grid(True)

    return (xtarget, ytarget, magnitude)

# -----------------------------------------------------------------------------
def local_laplacian_zscore(venue, results):
    """Plot the local laplacian zscore.

    Plot the grid showing the z-score for the local laplacian of the
    vertically-averaged head as color-coded markers. The colors are determined
    by the z-score and not the quantitative magnitude. However, the colormap
    places 0 in the middle. Thus, blue values (negative) indicate local net
    infiltration, red values (positive) indicate local net exfiltration.

    """
    xtarget = np.array([row[0][0] for row in results])
    ytarget = np.array([row[0][1] for row in results])

    bdry = venue.boundary()

    score = np.empty(xtarget.shape)
    for i, row in enumerate(results):
        evp = row[2]
        varp = row[3]

        laplacian = 2*(evp[0]+evp[1])
        stdev = 2*np.sqrt(varp[0, 0] + varp[1, 1] + 2*varp[0, 1])
        score[i] = min(max(laplacian/stdev, -3), 3)

    plt.figure(figsize=FIGSIZE)
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    divnorm = colors.TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3)
    plt.scatter(xtarget, ytarget, c=score, norm=divnorm, zorder=10, cmap="bwr")
    cbar = plt.colorbar()
    cbar.ax.set_title("z-score")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Local Vertically-averaged Laplacian Z-score", {"fontsize": 18})
    plt.grid(True)

    return (xtarget, ytarget, score)


# -----------------------------------------------------------------------------
def show_aquifers_by_venue(wells, venue, aquifers, parameters):
    """Plot the wells in the venue coded by aquifer.

    Plot the locations of the authorized wells in the `venue` that are
    completed in one or more of the identified `aquifers`, and that have a
    measured date between `after` and `before`. The plotted marker for a well
    is color-coded by the aquifer in which it is completed.

    Arguments
    ---------
    wells: Wells


    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated in `akeyaa.venues`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    aquifers : list
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system.

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
    aquifer_info : list[tuple] (aquifer_abbr, count)

        aquifer_abbr : str
            The four-character aquifer abbreviation string.
        count : int
            The number of wells in the associated aquifer type.

        The list is sorted in descending order by count.

    """
    firstyear = parameters["firstyear"]
    lastyear = parameters["lastyear"]
    bdry = venue.boundary()

    welldata = wells.fetch_by_venue(venue, aquifers, firstyear, lastyear)

    print(f"number of wells found = {len(welldata)}")

    xsel = [row[0][0] for row in welldata]
    ysel = [row[0][1] for row in welldata]
    asel = [row[2] for row in welldata]

    uaq, naq = np.unique(asel, return_counts=True)
    geo_hue, geo_hue_order, geo_palette = geologic_color_map(asel)

    plt.figure(figsize=FIGSIZE)
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")

    if len(xsel) > 0:
        sns.scatterplot(
            xsel, ysel, hue=geo_hue, hue_order=geo_hue_order, palette=geo_palette, zorder=10
        )

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Wells Coded By Aquifer", {"fontsize": 18})
    plt.grid(True)
    plt.show(block=False)

    aquifer_info = list(zip(uaq, naq))
    aquifer_info.sort(key=lambda tup: tup[1], reverse=True)
    return aquifer_info


def geologic_color_map(aquifers):
    """Map the aquifer codes to colors.

    This mapping of colors is based on the recommendations of numerous
    geologists and academics.

    Parameters
    ----------
    aquifers : list
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system.

    Returns
    -------
    geo_hue : list[str]
        List of the color category for each aquifer.

    geo_hue_order : list[str]
        List of geologically-related color categories in order.

    geo_palette : dict{str : str}
        Dictionary of colors for each geologically-related color category.

    """

    # C D I K M O P Q R U
    geo_hue_order = ["Qxxx", "Kxxx", "Dxxx", "Oxxx", "Cxxx", "Pxxx", "Mxxx", "other"]
    geo_palette = {
        "Qxxx": "gold",
        "Kxxx": "goldenrod",
        "Dxxx": "sienna",
        "Oxxx": "teal",
        "Cxxx": "limegreen",
        "Pxxx": "crimson",
        "Mxxx": "cornflowerblue",
        "other": "darkblue",
    }

    geo_hue = []
    for aqui in aquifers:
        if aqui[0] in {"Q", "K", "D", "O", "C", "P", "M"}:
            geo_hue.append(aqui[0] + "xxx")
        else:
            geo_hue.append("other")

    return (geo_hue, geo_hue_order, geo_palette)
