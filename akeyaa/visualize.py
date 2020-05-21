"""
Akeyaa visualization tools.

Functions
---------
visualize_results(results, poly)
    Plot the results.

retrieve_results(filename)
    Retrieve the results from the specified pickle file.

aquifer_by_county(cty_abbr, aquifer_list=None)
    Plot the county well data coded by aquifer.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
20 May 2020
"""

import pickle
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from get_data import get_county_code, get_well_data_by_county, get_county_polygon, get_county_name
from smith_distribution import smith_pdf


# -----------------------------------------------------------------------------
def visualize_results(results, poly, header):
    """
    Plot the results.

    Arguments
    ---------
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
            varaince/covariance matrix of the parameters.

    poly : arcpy.Polygon
        County polygon.
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm

    header : tuple
        (aquifer_list, cty_abbr, radius, reqnum, spacing, stde)
        See the list of arguments for akeyaa.by_county for details.
    """
    xbdry = [pnt.X for pnt in poly.getPart(0)]
    ybdry = [pnt.Y for pnt in poly.getPart(0)]

    x = np.empty((len(results), ))
    y = np.empty((len(results), ))

    n = np.empty((len(results), ), dtype='int')

    m = np.empty((len(results), ))
    u = np.empty((len(results), ))
    v = np.empty((len(results), ))

    r = np.empty((len(results), ))

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

        # varp = row[4]
        # s = 2 * np.sqrt(varp[0,0] + varp[1,1] + 2*varp[0,1])
        r[i] = -2*(evp[1]+evp[2])

    rlim = np.max(np.abs(r))

    cty_abbr = header[1]
    cty_name = get_county_name(cty_abbr)

    #------------------------
    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    plt.scatter(x, y, c=n, zorder=10, cmap='GnBu')
    cbar = plt.colorbar()
    cbar.ax.set_title('Count [#]')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('{0}: Number of Wells Used'.format(cty_name), {'fontsize' : 24})
    plt.grid(True)

    #------------------------
    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    plt.scatter(x, y, c=r, zorder=10, vmin=-rlim, vmax=rlim, cmap='bwr')
    cbar = plt.colorbar()
    cbar.ax.set_title('N/(kH) [1/m]')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('{0} County: Relative Recharge'.format(cty_name), {'fontsize' : 24})
    plt.grid(True)

    #------------------------
    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    plt.quiver(x, y, u, v, m, width=0.0018, zorder=10, cmap='magma')
    cbar = plt.colorbar()
    cbar.ax.set_title('Q/(kH) [.]')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('{0} County: Local Flow Directions'.format(cty_name), {'fontsize' : 24})
    plt.grid(True)

    #------------------------
    plt.draw_all()


# -----------------------------------------------------------------------------
def retrieve_results(filename):
    """
    Retrieve the results from the specified pickle file.

    Arguments
    ---------
    filename : str
        The name of the pickle file.

    Returns
    -------
    (results, poly, header) : tuple
        o   results : list of tuples
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
                    varaince/covariance matrix of the parameters.

        o   poly : arcpy.Polygon
                County polygon.
                https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm

        o   header : tuple
                (aquifer_list, cty_abbr, radius, reqnum, spacing, stde)
                See the list of arguments for akeyaa.by_county for details.

    """
    (header, results) = pickle.load(open(filename, 'rb'))
    poly = get_county_polygon(header[1])

    return (results, poly, header)


# -----------------------------------------------------------------------------
def aquifer_by_county(cty_abbr, aquifer_list=None):
    """
    Plot the county well data locations coded by aquifer.

    Arguments
    ---------
    cty_abbr : str
        The four-character county abbrevaition string.

    aquifer_list : list (optional)
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included.

    Returns
    -------
    aq_info : list of tuples
        Each element in the list is a tuple (aq_abbr, count)
        -- aq_abbr : str
            The four-character aquifer abbreviation.
        -- count : int
            The number of wells in the associated aquifer type.
    """
    cty_code = get_county_code(cty_abbr)
    cty_name = get_county_name(cty_abbr)
    welldata = get_well_data_by_county(cty_code, aquifer_list)

    poly = get_county_polygon(cty_abbr)
    xbdry = [pnt.X for pnt in poly.getPart(0)]
    ybdry = [pnt.Y for pnt in poly.getPart(0)]

    x = [row[0][0] for row in welldata]
    y = [row[0][1] for row in welldata]
    aq = [row[3] for row in welldata]

    uaq, naq = np.unique(aq, return_counts=True)

    plt.figure()
    plt.axis('equal')

    plt.fill(xbdry, ybdry, '0.90')
    sns.scatterplot(x, y, hue=aq, hue_order=uaq.tolist(), zorder=10)

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title('{0} County: Well Data Coded By Aquifer'.format(cty_name))

    return [(uaq[i], naq[i]) for i in range(len(uaq))]


# -----------------------------------------------------------------------------
def pdf_plot(mu, sigma):

    # Create the sweep of angles at which the pdf is evaluated.
    alpha = np.linspace(0, 2*np.pi, 361)

    # Compute the posterior distribution using all of the data.
    f = smith_pdf(alpha, mu, sigma)

    plt.figure()
    plt.polar(alpha, f*np.pi/180.)
    plt.title("Shith's Distribution PDF")