"""
Akeyaa analyses functions.

Functions
---------
shortcut(what, aquifer_list=None, radius=3000, reqnum=25, spacing=1000,
              method='RLM', pklzfile=None):
    A shortcut way to run Akeyaa analysis and visualization with mostly
    default parameters.

by_county(aquifer_list, cty_abbr, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified county.

by_watershed(aquifer_list, wtrs_code, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified watershed.

by_subregion(subr_name, aquifer_list, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified hydrologic subregion.

by_polygon(aquifer_list, poly, radius, reqnum, spacing, method):
    Compute the full Akeyaa analysis across the specified polygon.

fit_conic(x, y, z, method)
    Fit the conic potential model using requested method.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
25 May 2020
"""

import bz2
from datetime import datetime
import os
import pickle
import time
import numpy as np
from scipy import spatial
import arcpy
import statsmodels.api as sm

from getdata import get_well_data, NotFoundError
from getdata import get_county_code, get_county_name, get_county_polygon
from getdata import get_watershed_name, get_watershed_polygon
from getdata import get_subregion_name, get_subregion_polygon

from visualize import visualize_results


# -----------------------------------------------------------------------------
class Error(Exception):
    """
    Local base exception.
    """


class UnknownMethodError(Error):
    """
    The requested method is not supported.
    """

# -----------------------------------------------------------------------------
def shortcut(what, aquifer_list=None, radius=3000, reqnum=25, spacing=1000,
              method='RLM', pklzfile=None):
    """
    A shortcut way to run Akeyaa analysis and visualization with mostly
    all default parameters.

    The selection, 'what', can be a county abbreviation, a watershed name, or
    a watershed code. This function the appropriate version of the akeyaa
    engine (by_county or by_watershed), creates a temporary .pklz file to
    store the results, calls visualize_results, and then deletes the temporary
    file.

    Arguments
    ---------
    what : str
        -- A 4-character county abbreviation string, or
        -- a watershed name as encoded in WBD_National_GDB.gd, or
        -- a 10-digit watershed code as a string (HUC10)

    aquifer_list : list (optional)
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included. Default = None.

    radius : float (optional)
        Search radius for neighboring wells. radius > 0. Default = 3000 [m].

    reqnum : int (optional)
        Required number of neighboring wells. If fewer are found, the target
        location is skipped. reqnum > 6. Default = 25.

    spacing : float (optional)
        Grid spacing for target locations across the county. spacing > 0.
        Default = 1000 [m].

    method : str (optional)
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.
        Default = 'RLM'.

    pklzfile : str (optional)
        Compressed pickle file path/name. If None, the output file is not
        created. Default = None.

    Returns
    -------
    None

    Notes
    -----
    o   I do not know if there are any watershed names that are also subregion
        names.

    """
    # Initialize the stopwatch.
    start_time = time.time()

    # Make a pickle filename, if none is given.
    if pklzfile is None:
        pklzfile ='Akeyya' + datetime.now().strftime('%Y%m%dT%H%M%S') + '.pklz'
        remove_flag = True
    else:
        remove_flag = False

    # Is 'what' is a cty_abbr?
    try:
        _ = get_county_code(what)
        by_county(what, aquifer_list, radius, reqnum, spacing, method, pklzfile)
        visualize_results(pklzfile)
        if remove_flag:
            os.remove(pklzfile)
        print('Elapsed time = {0:.4f} seconds'.format(time.time() - start_time))
        return

    except NotFoundError:
        pass

    except:
        raise

    # Is 'what' is a watershed code?
    try:
        _ = get_watershed_name(what)
        by_watershed(what, aquifer_list, radius, reqnum, spacing, method, pklzfile)
        visualize_results(pklzfile)
        if remove_flag:
            os.remove(pklzfile)
        print('Elapsed time = {0:.4f} seconds'.format(time.time() - start_time))
        return

    except NotFoundError:
        pass

    except:
        raise

    # Is 'what' is a subregion code?
    try:
        _ = get_subregion_name(what)
        by_subregion(what, aquifer_list, radius, reqnum, spacing, method, pklzfile)
        visualize_results(pklzfile)
        if remove_flag:
            os.remove(pklzfile)
        print('Elapsed time = {0:.4f} seconds'.format(time.time() - start_time))
        return

    except NotFoundError:
        pass

    except:
        raise

    # Apparently, 'what' is unknown...
    raise NotFoundError


# -----------------------------------------------------------------------------
def by_county(cty_abbr, aquifer_list, radius, reqnum, spacing, method,
              pklzfile=None):
    """
    Compute the full Akeyaa analysis across the specified county.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified county. The grid is defined by <spacing>. The
    analysis is carried out using the wells in the specified aquifer(s) only.
    The analysis may use wells in neighboring counties.

    Arguments
    ---------
    cty_abbr : str
        The 4-character county abbreviation string.

    aquifer_list : list
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included.

    radius : float
        Search radius for neighboring wells. radius > 0.

    reqnum : int
        Required number of neighboring wells. If fewer are found, the target
        location is skipped. reqnum > 6.

    spacing : float
        Grid spacing for target locations across the county. spacing > 0.

    method : str
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.

    pklzfile : str (optional)
        Compressed pickle file path/name. If None, the output file is not
        created. Default = None.

    Returns
    -------
    results : list of tuples (xtarget, ytarget, n, evp, varp)
    -- xtarget : float
           x-coordinate of target location.
    -- ytarget : float
           y-coordinate of target location.
    -- n : int
           number of neighborhood wells used in the local analysis.
    -- evp : ndarray, shape=(6,1)
           expected value vector of the prarameters.
    -- varp : ndarray, shape=(6,6)
           approximate variance/covariance matrix of the parameters.

    Notes
    -----
    o   Note, data from outside of the county may also used in the
        computations. However, only data from the Minnesota CWI are
        considered.
    """

    # Get the county polygon.
    poly = get_county_polygon(cty_abbr)

    # Create the associated tile string.
    cty_name = get_county_name(cty_abbr)
    if aquifer_list is not None:
        title_str = '{0} County {1}: '.format(cty_name, aquifer_list)
    else:
        title_str = '{0} County [All]: '.format(cty_name)

    # Carry out the Akeyaa analisis.
    results = by_polygon(poly, aquifer_list, radius, reqnum, spacing, method)

    # If requested, save the run to a compressed pickle file.
    if pklzfile is not None:
        archive = {
            'aquifer_list' : aquifer_list,
            'cty_abbr' : cty_abbr,
            'cty_name' : cty_name,
            'radius' : radius,
            'reqnum' : reqnum,
            'spacing' : spacing,
            'method' : method,
            'title_str' : title_str,
            'poly' : poly,
            'results' : results
            }
        with bz2.open(pklzfile, 'wb') as fp:
            pickle.dump(archive, fp)

    return results


# -----------------------------------------------------------------------------
def by_watershed(wtrs_code, aquifer_list, radius, reqnum, spacing, method,
                 pklzfile=None):
    """
    Compute the full Akeyaa analysis across the specified hydrologic watershed.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified watershed. The grid is defined by <spacing>. The
    analysis is carried out using the wells in the specified aquifer(s) only.
    The analysis may use wells in neighboring watersheds.

    Arguments
    ---------
    wtrs_code : str
        The unique 10-digit number encoded as a string (HUC10).

    aquifer_list : list
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included.

    radius : float
        Search radius for neighboring wells. radius > 0.

    reqnum : int
        Required number of neighboring wells. If fewer are found, the target
        location is skipped. reqnum > 6.

    spacing : float
        Grid spacing for target locations across the county. spacing > 0.

    method : str
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.

    pklzfile : str (optional)
        Compressed pickle file path/name. If None, the output file is not
        created. Default = None.

    Returns
    -------
    results : list of tuples (xtarget, ytarget, n, evp, varp)
    -- xtarget : float
           x-coordinate of target location.
    -- ytarget : float
           y-coordinate of target location.
    -- n : int
           number of neighborhood wells used in the local analysis.
    -- evp : ndarray, shape=(6,1)
           expected value vector of the prarameters.
    -- varp : ndarray, shape=(6,6)
           approximate variance/covariance matrix of the parameters.

    Notes
    -----
    o The subregion names are NOT unique.
    """

    # Get the watershed polygon.
    wtrs_name = get_watershed_name(wtrs_code)
    poly = get_watershed_polygon(wtrs_code)

    # Create the associated tile string.
    if aquifer_list is not None:
        title_str = '{0} Watershed {1}: '.format(wtrs_name, aquifer_list)
    else:
        title_str = '{0} Watershed [All]: '.format(wtrs_name)

    # Carry out the Akeyaa analisis.
    results = by_polygon(poly, aquifer_list, radius, reqnum, spacing, method)

    # If requested, save the run to a compressed pickle file.
    if pklzfile is not None:
        archive = {
            'aquifer_list' : aquifer_list,
            'wtrs_code' : wtrs_code,
            'wtrs_name' : wtrs_name,
            'radius' : radius,
            'reqnum' : reqnum,
            'spacing' : spacing,
            'method' : method,
            'title_str' : title_str,
            'poly' : poly,
            'results' : results
            }
        with bz2.open(pklzfile, 'wb') as fp:
            pickle.dump(archive, fp)

    return results


# -----------------------------------------------------------------------------
def by_subregion(subr_code, aquifer_list, radius, reqnum, spacing, method,
                 pklzfile=None):
    """
    Compute the full Akeyaa analysis across the specified hydrologic subregion.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified subregion. The grid is defined by <spacing>. The
    analysis is carried out using the wells in the specified aquifer(s) only.
    The analysis may use wells in neighboring subregions.

    Arguments
    ---------
    subr_code : str
        The unique 10-digit number encoded as a string (HUC8).

    aquifer_list : list
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included.

    radius : float
        Search radius for neighboring wells. radius > 0.

    reqnum : int
        Required number of neighboring wells. If fewer are found, the target
        location is skipped. reqnum > 6.

    spacing : float
        Grid spacing for target locations across the county. spacing > 0.

    method : str
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.

    pklzfile : str (optional)
        Compressed pickle file path/name. If None, the output file is not
        created. Default = None.

    Returns
    -------
    results : list of tuples (xtarget, ytarget, n, evp, varp)
    -- xtarget : float
           x-coordinate of target location.
    -- ytarget : float
           y-coordinate of target location.
    -- n : int
           number of neighborhood wells used in the local analysis.
    -- evp : ndarray, shape=(6,1)
           expected value vector of the prarameters.
    -- varp : ndarray, shape=(6,6)
           approximate variance/covariance matrix of the parameters.

    Notes
    -----
    o The subregion names are NOT unique.
    """

    # Get the subregion polygon.
    subr_name = get_subregion_name(subr_code)
    poly = get_subregion_polygon(subr_code)

    # Create the associated tile string.
    if aquifer_list is not None:
        title_str = '{0} Subregion {1}: '.format(subr_name, aquifer_list)
    else:
        title_str = '{0} Subregion [All]: '.format(subr_name)

    # Carry out the Akeyaa analisis.
    results = by_polygon(poly, aquifer_list, radius, reqnum, spacing, method)

    # If requested, save the run to a compressed pickle file.
    if pklzfile is not None:
        archive = {
            'aquifer_list' : aquifer_list,
            'subr_name' : subr_name,
            'subr_code' : subr_code,
            'radius' : radius,
            'reqnum' : reqnum,
            'spacing' : spacing,
            'method' : method,
            'title_str' : title_str,
            'poly' : poly,
            'results' : results
            }
        with bz2.open(pklzfile, 'wb') as fp:
            pickle.dump(archive, fp)

    return results


# -----------------------------------------------------------------------------
def by_polygon(poly, aquifer_list, radius, reqnum, spacing, method):
    """
    Compute the full Akeyaa analysis across the specified polygon.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified polygon. The grid is defined by <spacing>. The
    analysis is carried out using the wells in the specified aquifer(s) only.
    The analysis may use wells in neighboring polygons.

    Arguments
    ---------
    aquifer_list : list
        List of four-character aquifer abbreviation strings. If none, then all
        available aquifers will be included.

    poly : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm

    radius : float
        Search radius for neighboring wells. radius > 0.

    reqnum :
        Required number of neighboring wells. If fewer are found, the target
        location is skipped. reqnum > 6.

    spacing : float
        Grid spacing for target locations across the county. spacing > 0.

    method : str
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.

    Returns
    -------
    results : list of tuples (xtarget, ytarget, n, evp, varp)
    -- xtarget : float
           x-coordinate of target location.
    -- ytarget : float
           y-coordinate of target location.
    -- n : int
           number of neighborhood wells used in the local analysis.
    -- evp : ndarray, shape=(6,1)
           expected value vector of the prarameters.
    -- varp : ndarray, shape=(6,6)
           approximate variance/covariance matrix of the parameters.

    Notes
    -----
    o   Note, data from outside of the polygon may also used in the
        computations.
    """

    # Get all of the located static water level data from across the state
    # in the selected aquifers and create a KD search tree.
    welldata = get_well_data(aquifer_list)
    x = np.array([well[0][0] for well in welldata])
    y = np.array([well[0][1] for well in welldata])
    z = np.array([well[1] for well in welldata])

    tree = spatial.cKDTree(np.column_stack((x, y)))

    # Create the grid of target locations across the specified polygon.
    nx = int(np.ceil((poly.extent.XMax - poly.extent.XMin)/spacing) + 1)
    xg = np.linspace(poly.extent.XMin, poly.extent.XMin + (nx-1)*spacing, nx)

    ny = int(np.ceil((poly.extent.YMax - poly.extent.YMin)/spacing) + 1)
    yg = np.linspace(poly.extent.YMin, poly.extent.YMin + (ny-1)*spacing, ny)

    # Process every grid node as a potential target.
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
                    xactive = x[active_wells]
                    yactive = y[active_wells]
                    zactive = z[active_wells]

                    evp, varp = fit_conic(xactive-xtarget, yactive-ytarget, zactive, method)
                    results.append((xtarget, ytarget, n, evp, varp))

    return results


#------------------------------------------------------------------------------
def fit_conic(x, y, z, method='RLM'):
    """
    Fit the conic potential model using robust linear regression.

    Arguments
    ---------
    x : ndarray, shape=(N, )
        x-coordinates of observation locations [m].

    y : ndarray, shape=(N, )
        y-coordinates of observation locations [m].

    z : ndarray, shape=(N, )
        observed head values [m].

    method : str (optional)
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.
            Default = 'RLM'.

    Returns
    -------
    evp : ndarray, shape=(6, )
        The expected value vector for the model parameters.

    varp : ndarray, shape=(6, 6)
        The variance matrix for the model parameters.

    Raises
    ------
    None.

    Notes
    -----
    o   The underlying model is
            z = p[0]*x**2 + p[1]*y**2 + p[2]*x*y + p[3]*x + p[4]*y + p[5] + e

    o   The variable names in this function follow the naming convention in the
        associated white paper, and not with Python convention.

    o   Most of the work is done by the statsmodels library.
    """

    # Set up the coefficient matrix.
    n = len(x)
    X = np.zeros((n, 6))

    for i in range(n):
        X[i, 0] = x[i]**2
        X[i, 1] = y[i]**2
        X[i, 2] = x[i]*y[i]
        X[i, 3] = x[i]
        X[i, 4] = y[i]
        X[i, 5] = 1.0

    # Apply the statsmodels tools.
    if method == 'OLS':
        ols_model = sm.OLS(z, X)
        ols_results = ols_model.fit()

        evp = ols_results.params
        varp = ols_results.cov_params()

    elif method == 'RLM':
        rlm_model = sm.RLM(z, X, M=sm.robust.norms.TukeyBiweight())
        rlm_results = rlm_model.fit()

        evp = rlm_results.params
        varp = rlm_results.bcov_scaled

    else:
       raise UnknownMethodError

    return (evp, varp)
