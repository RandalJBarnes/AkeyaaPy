"""Plot the geolocial information within a venue."""
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from akeyaa.wells import Wells

__author__ = "Randal J Barnes"
__version__ = "24 July 2020"


class Error(Exception):
    """The base exception for the module."""

class EmptySelectionError(Error):
    """There are no wells in the selection."""


def aquifers_by_venue(venue, aquifers=None, after=None, before=None):
    """Plot the wells in the venue coded by aquifer.

    Plot the locations of the authorized wells in the `venue` that are
    completed in one or more of the identified `aquifers`, and that have a
    measured date between `after` and `before`. The plotted marker for a well
    is color-coded by the aquifer in which it is completed.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated in `akeyaa.venues`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

    after : int
        Earliest measurement date to use; written as YYYYMMDD.

    before : int
        Latest measurement date to use; written as YYYYMMDD.

    Returns
    -------
    aquifer_info : list[tuple] (aquifer_abbr, count)

        aquifer_abbr : str
            The four-character aquifer abbreviation string.
        count : int
            The number of wells in the associated aquifer type.

        The list is sorted in descending order by count.

    """
    bdry = venue.boundary()
    wells = Wells()

    welldata = wells.fetch_by_venue(venue, aquifers, after, before)

    xsel = [row[0][0] for row in welldata]
    ysel = [row[0][1] for row in welldata]
    asel = [row[2] for row in welldata]

    if len(xsel) == 0:
        raise EmptySelectionError

    uaq, naq = np.unique(asel, return_counts=True)
    geo_hue, geo_hue_order, geo_palette = geologic_color_map(asel)

    plt.figure()
    plt.axis("equal")

    plt.fill(bdry[:, 0], bdry[:, 1], "0.80")
    sns.scatterplot(
        xsel, ysel, hue=geo_hue, hue_order=geo_hue_order, palette=geo_palette, zorder=10
    )

    plt.xlabel("Easting [m]")
    plt.ylabel("Northing [m]")
    plt.title(venue.fullname() + " Wells Coded By Aquifer", {"fontsize": 24})
    plt.grid(True)

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
