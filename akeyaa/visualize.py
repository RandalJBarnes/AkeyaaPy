"""
Akeyaa visualization tools.

Functions
---------
visualize_results(pklzfile)
    Plot the results.

aquifer_by_county(cty_abbr, aquifer_list=None)
    Plot the county well data coded by aquifer.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
24 May 2020
"""

import bz2
import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import get_data
from smith_distribution import smith_pdf


# -----------------------------------------------------------------------------
def visualize_results(pklzfile):
    """
    Plot the results.

    Arguments
    ---------
    pklzfile : str
        Compressed pickle file path/name for the run.
    """

    # Get the run data from the pickle file.
    with bz2.open(pklzfile, 'rb') as fp:
        archive = pickle.load(fp)

    title_str = archive.get('title_str')
    poly = archive.get('poly')
    results = archive.get('results')

    # Get the polygon boundary information.
    xbdry = [pnt.X for pnt in poly.getPart(0)]
    ybdry = [pnt.Y for pnt in poly.getPart(0)]

    # Extract and collate the run information.
    x = np.empty((len(results),))
    y = np.empty(x.shape)
    n = np.empty(x.shape, dtype='int')
    m = np.empty(x.shape)
    u = np.empty(x.shape)
    v = np.empty(x.shape)

    for i, row in enumerate(results):
        x[i] = row[0]
        y[i] = row[1]
        n[i] = row[2]

        evp = row[3]
        Qx = -evp[3]
        Qy = -evp[4]

        m[i] = np.hypot(Qx, Qy)
        u[i] = Qx/np.hypot(Qx, Qy)
        v[i] = Qy/np.hypot(Qx, Qy)

    #------------------------
    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    plt.quiver(x, y, u, v, m, width=0.0018, zorder=10, cmap='magma')
    cbar = plt.colorbar()
    cbar.ax.set_title('Q/(kH) [.]')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title(title_str + 'Local Flow Directions', {'fontsize' : 24})
    plt.grid(True)

    #------------------------
    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    plt.scatter(x, y, c=n, zorder=10, cmap='GnBu')
    cbar = plt.colorbar()
    cbar.ax.set_title('Count [#]')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title(title_str + 'Number of Local Wells', {'fontsize' : 24})
    plt.grid(True)

    #------------------------
    plt.draw_all()



# -----------------------------------------------------------------------------
def aquifers_in_county(cty_abbr, aquifer_list=None):
    """
    Plot the county well data locations coded by aquifer.

    Arguments
    ---------
    cty_abbr : str
        The 4-character county abbreviation string.

    aquifer_list : list (optional)
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included. Default = None.

    Returns
    -------
    Returns
    -------
    aq_info : list of tuples
        Each element in the list is a tuple (aq_abbr, count)
        -- aq_abbr : str
            The four-character aquifer abbreviation.
        -- count : int
            The number of wells in the associated aquifer type.
        The list is sorted in descending order by count.
    """

    # Get the county polygon.
    poly = get_data.get_county_polygon(cty_abbr)

    # Create the associated tile string.
    cty_name = get_data.get_county_name(cty_abbr)
    if aquifer_list is not None:
        title_str = '{0} County {1}: '.format(cty_name, aquifer_list)
    else:
        title_str = '{0} County [All]: '.format(cty_name)

    # Find and plot the well locations, coded by aquifer.
    aq_info = aquifers_in_polygon(poly, aquifer_list, title_str)

    return aq_info


# -----------------------------------------------------------------------------
def aquifers_in_watershed(wtrs_code, aquifer_list=None):
    """
    Plot the watershed well data locations coded by aquifer.

    Arguments
    ---------
    cty_abbr : str
        The 4-character county abbreviation string.

    aquifer_list : list (optional)
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included. Default = None.

    Returns
    -------
    Returns
    -------
    aq_info : list of tuples
        Each element in the list is a tuple (aq_abbr, count)
        -- aq_abbr : str
            The four-character aquifer abbreviation.
        -- count : int
            The number of wells in the associated aquifer type.
        The list is sorted in descending order by count.
    """

    # Get the watershed polygon.
    poly = get_data.get_watershed_polygon(wtrs_code)

    # Create the associated tile string.
    wtrs_name = get_data.get_watershed_name(wtrs_code)
    if aquifer_list is not None:
        title_str = '{0} Watershed {1}: '.format(wtrs_name, aquifer_list)
    else:
        title_str = '{0} Watershed [All]: '.format(wtrs_name)

    # Find and plot the well locations, coded by aquifer.
    aq_info = aquifers_in_polygon(poly, title_str, aquifer_list)

    return aq_info


# -----------------------------------------------------------------------------
def aquifers_in_polygon(poly, title_str, aquifer_list=None):
    """
    Plot the polygon well data locations coded by aquifer.

    Arguments
    ---------
    poly : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm

    aquifer_list : list (optional)
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included. Default = None.

    title_str : str
        The identifiying generic title prefix.

    Returns
    -------
    aq_info : list of tuples
        Each element in the list is a tuple (aq_abbr, count)
        -- aq_abbr : str
            The four-character aquifer abbreviation.
        -- count : int
            The number of wells in the associated aquifer type.
        The list is sorted in descending order by count.
    """

    # Get the polygon boundary information.
    xbdry = [pnt.X for pnt in poly.getPart(0)]
    ybdry = [pnt.Y for pnt in poly.getPart(0)]

    # Get the data for wells in the polygon.
    welldata = get_data.get_well_data_by_polygon(poly, aquifer_list)

    x = [row[0][0] for row in welldata]
    y = [row[0][1] for row in welldata]
    aq = [row[3] for row in welldata]

    # Determine a list of unique aquifers present and their associated counts.
    uaq, naq = np.unique(aq, return_counts=True)

    active_aq = [(uaq[i], naq[i]) for i in range(len(uaq))]
    active_aq.sort(key = lambda tup: tup[1], reverse = True)

    # Plot the well locations coded by aquifer.
    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    sns.scatterplot(x, y, hue=aq, hue_order=uaq.tolist(), zorder=10)

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title(title_str + 'Wells Coded By Aquifer', {'fontsize' : 24})

    return active_aq


# -----------------------------------------------------------------------------
def pdf_plot(mu, sigma):
    """
    Make a polar plot of the specified Smith's distribution.
    """

    # Create the sweep of angles at which the pdf is evaluated.
    alpha = np.linspace(0, 2*np.pi, 361)

    # Compute the posterior distribution using all of the data.
    f = smith_pdf(alpha, mu, sigma)

    plt.figure()
    plt.polar(alpha, f*np.pi/180.)
    plt.title("Smith's Distribution PDF")