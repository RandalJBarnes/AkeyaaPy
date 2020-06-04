"""Akeyaa visualization tools.

Functions
---------
aquifers_by_venue(venue, aquifers)
    Plot the wells in the vnue coded by aquifer.

geologic_color_map(aquifers)
    Map the aquifer code to colors.

whereis(venue):
    Plot the venue's domain over the state's ploygon.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
04 June 2020
"""

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

import gis
import venues


# -----------------------------------------------------------------------------
class Error(Exception):
    """
    The base exception for the module.
    """


class EmptySelectionError(Error):
    """
    There are no wells in the selection.
    """

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

    bdry = venue.domain.boundary()
    welldata = gis.get_well_data_by_domain(venue.domain)

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
    geo_hue, geo_hue_order, geo_palette = geologic_color_map(asel)

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.90")
    sns.scatterplot(xsel, ysel,
                    hue=geo_hue, hue_order=geo_hue_order, palette=geo_palette,
                    zorder=10)

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Wells Coded By Aquifer", {"fontsize": 24})

    aquifer_info = list(zip(uaq, naq))
    aquifer_info.sort(key=lambda tup: tup[1], reverse=True)
    return aquifer_info


# -----------------------------------------------------------------------------
def geologic_color_map(aquifers):
    """Map the aquifer code to colors."""

    geo_hue_order = ["Qxxx", "Kxxx", "Dxxx", "Oxxx", "Cxxx", "Pxxx", "Mxxx", "other"]
    geo_palette = {
        "Qxxx": "gold",
        "Kxxx": "goldenrod",
        "Dxxx": "sienna",
        "Oxxx": "teal",
        "Cxxx": "limegreen",
        "Pxxx": "crimson",
        "Mxxx": "cornflowerblue",
        "other": "darkblue"
    }

    geo_hue = []
    for aq in aquifers:
        if aq[0] in {"Q", "K", "D", "O", "C", "P", "M"}:
            geo_hue.append(aq[0] + 'xxx')
        else:
            geo_hue.append('other')

    return (geo_hue, geo_hue_order, geo_palette)



# -----------------------------------------------------------------------------
def whereis(venue):
    """Plot the venue's domain over the state's ploygon.

    Arguments
    ---------
    venue : a concrete subclass of venues.Venue (i.e. City)

    Returns
    -------
    None
    """

    state = venues.State()
    state_bdry = state.domain.boundary()
    venue_bdry = venue.domain.boundary()

    plt.figure()
    plt.axis("equal")

    plt.fill(state_bdry[:, 0], state_bdry[:, 1], "0.90")
    plt.fill(venue_bdry[:, 0], venue_bdry[:, 1], "b")

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname(), {"fontsize": 24})
    plt.grid(True)
