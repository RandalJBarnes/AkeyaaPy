"""
Akeyaa analyses functions.

Functions
---------
by_county(aquifer_list, cty_abbr, radius, reqnum, spacing, stde):
    Compute the full Akeyaa analysis across the specified county.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
20 May 2020
"""

from datetime import datetime
import pickle
import numpy as np
from scipy import spatial
import arcpy

from conic_potential import fit_conic
from get_data import get_well_data, get_county_polygon


# -----------------------------------------------------------------------------
def by_county(aquifer_list, cty_abbr, radius, reqnum, spacing, stde):
    """
    Compute the full Akeyaa analysis across the specified county.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified county. The grid is defined by <spacing>. The analysis
    is carried out using the wells in the specified aquifer(s) only. The
    analysis may use wells in adjacent counties.

    Arguments
    ---------
    aquifer_list : list
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included.

    cty_abbr : str
        The four-character county abbreviation string.

    radius : float
        Search radius for neighboring wells. radius > 0.

    reqnum :
        Required number of neighboring wells. If fewer are found, the target
        location is skipped. reqnum > 6.

    spacing : float
        Grid spacing for target locations across the county. spacing > 0.

    stde : float
        Common standard deviaiton of the obsered heads. stde > 0.

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
                See the list of arguments for details.

    Notes
    -----
    o   Data outside of the county are also used in the computations.

    o   TODO: include well-specific standard deviations.
    """

    # Get all of the located QBAA static water level data from around the
    # state and create a KD search tree.
    well_list = get_well_data(aquifer_list)
    xyz = np.array([[well[0][0], well[0][1], well[1]] for well in well_list])
    tree = spatial.cKDTree(xyz[:, 0:2])

    # Create the grid of target locations across the specified county.
    poly = get_county_polygon(cty_abbr)

    nx = int(np.ceil((poly.extent.XMax - poly.extent.XMin)/spacing) + 1)
    xg = np.linspace(poly.extent.XMin, poly.extent.XMin + (nx-1)*spacing, nx)

    ny = int(np.ceil((poly.extent.YMax - poly.extent.YMin)/spacing) + 1)
    yg = np.linspace(poly.extent.YMin, poly.extent.YMin + (ny-1)*spacing, ny)

    # Process every township in Minnesota.
    results = []

    for i in range(ny):
        for j in range(nx):
            xtarget = xg[j]
            ytarget = yg[i]

            if poly.contains(arcpy.Point(xtarget, ytarget)):
                active_wells = tree.query_ball_point([xtarget, ytarget], radius)
                n = len(active_wells)

                # Carryout the weighted least squares regression.
                if n >= reqnum:
                    x = np.array([xyz[i, 0] for i in active_wells])
                    y = np.array([xyz[i, 1] for i in active_wells])
                    z = np.array([xyz[i, 2] for i in active_wells])
                    s = stde*np.ones(len(x))

                    evp, varp = fit_conic(x-xtarget, y-ytarget, z, s)
                    results.append((xtarget, ytarget, n, evp, varp))

    # Save the results to a file.
    header = (aquifer_list, cty_abbr, radius, reqnum, spacing, stde)

    filename = 'Akeyaa' + datetime.now().strftime('%Y%m%dT%H%M%S') + '.pickle'
    pickle.dump((header, results), open(filename, 'wb'))

    return (results, poly, header)
