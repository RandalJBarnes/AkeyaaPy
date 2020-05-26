"""
Akeyaa analyses functions.

Functions
---------
shortcut(what, aquifers=None, radius=3000, reqnum=25, spacing=1000,
              method='RLM', pklzfile=None):
    A shortcut way to run Akeyaa analysis and visualization with mostly
    default parameters.

by_county(aquifers, cty_abbr, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified county.

by_watershed(aquifers, wtrs_code, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified watershed.

by_subregion(subr_name, aquifers, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified hydrologic subregion.

by_polygon(aquifers, polygon, radius, reqnum, spacing, method):
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
import datetime
import os
import pickle
import time
import numpy as np
import scipy
import statsmodels.api as sm
import arcpy

import getdata
import visualize


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
def shortcut(what, aquifers=None, radius=3000, reqnum=25, spacing=1000,
             method='RLM', pklzfile=None):
    """
    A shortcut to run Akeyaa analysis and visualization.

    The selection, 'what', can be a county abbreviation, a watershed name, or
    a watershed code. This function the appropriate version of the akeyaa
    engine (by_county or by_watershed), creates a temporary .pklz file to
    store the results, calls visualize_results, and then deletes the temporary
    file.

    Parameters
    ----------
    what : str
        -- a 4-character county abbreviation string,
        -- a 10-digit watershed number encoded as a string (HUC10), or
        -- an 8-digit subregion number encoded as a string (HUC8).

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

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
    o   Beware! Watershed names are not unique.
    """

    # Initialize the stopwatch.
    start_time = time.time()

    # Make a pickle filename, if none is given.
    if pklzfile is None:
        pklzfile = (
            'Akeyya'
            + datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
            + '.pklz')
        remove_flag = True
    else:
        remove_flag = False

    # Is 'what' is a cty_abbr?
    try:
        _ = getdata.get_county_code(what)
        by_county(what, aquifers, radius, reqnum, spacing, method, pklzfile)
        visualize.load_and_visualize_results(pklzfile)
        if remove_flag:
            os.remove(pklzfile)
        print('Elapsed time = {0:.4f} seconds'
              .format(time.time() - start_time))
        return

    except getdata.NotFoundError:
        pass

    # Is 'what' is a watershed code?
    try:
        _ = getdata.get_watershed_name(what)
        by_watershed(what, aquifers, radius, reqnum, spacing, method, pklzfile)
        visualize.load_and_visualize_results(pklzfile)
        if remove_flag:
            os.remove(pklzfile)
        print('Elapsed time = {0:.4f} seconds'
              .format(time.time() - start_time))
        return

    except getdata.NotFoundError:
        pass

    # Is 'what' is a subregion code?
    try:
        _ = getdata.get_subregion_name(what)
        by_subregion(what, aquifers, radius, reqnum, spacing, method, pklzfile)
        visualize.load_and_visualize_results(pklzfile)
        if remove_flag:
            os.remove(pklzfile)
        print('Elapsed time = {0:.4f} seconds'
              .format(time.time() - start_time))
        return

    except getdata.NotFoundError:
        pass

    # Apparently, 'what' is unknown...
    raise getdata.NotFoundError


# -----------------------------------------------------------------------------
def by_county(cty_abbr, aquifers, radius, reqnum, spacing, method,
              pklzfile=None):
    """
    Compute the full Akeyaa analysis across the specified county.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified county. The grid is defined by <spacing>. The
    analysis is carried out using the wells in the specified aquifer(s) only.
    The analysis may use wells in neighboring counties.

    Parameters
    ----------
    cty_abbr : str
        The 4-character county abbreviation string.

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

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
    results : list of tuples
        (xtarget, ytarget, n, evp, varp)
        -- xtarget : float
               x-coordinate of target location.
        -- ytarget : float
               y-coordinate of target location.
        -- n : int
               number of neighborhood wells used in the local analysis.
        -- evp : ndarray, shape=(6, 1)
               expected value vector of the prarameters.
        -- varp : ndarray, shape=(6, 6)
               variance/covariance matrix of the parameters.

    Notes
    -----
    o   Note, data from outside of the county may also used in the
        computations. However, only data from the Minnesota CWI are
        considered.
    """

    # Get the county polygon.
    polygon = getdata.get_county_polygon(cty_abbr)

    # Create the associated tile string.
    cty_name = getdata.get_county_name(cty_abbr)
    if aquifers is not None:
        title_prefix = '{0} County {1}: '.format(cty_name, aquifers)
    else:
        title_prefix = '{0} County [All]: '.format(cty_name)

    # Carry out the Akeyaa analisis.
    results = by_polygon(polygon, aquifers, radius, reqnum, spacing, method)

    # If requested, save the run to a compressed pickle file.
    if pklzfile is not None:
        archive = {
            'aquifers': aquifers,
            'cty_abbr': cty_abbr,
            'cty_name': cty_name,
            'radius': radius,
            'reqnum': reqnum,
            'spacing': spacing,
            'method': method,
            'title_prefix': title_prefix,
            'polygon': polygon,
            'results': results
            }
        with bz2.open(pklzfile, 'wb') as fileobject:
            pickle.dump(archive, fileobject)

    return results


# -----------------------------------------------------------------------------
def by_watershed(wtrs_code, aquifers, radius, reqnum, spacing, method,
                 pklzfile=None):
    """
    Compute the full Akeyaa analysis across the specified hydrologic watershed.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified watershed. The grid is defined by <spacing>. The
    analysis is carried out using the wells in the specified aquifer(s) only.
    The analysis may use wells in neighboring watersheds.

    Parameters
    ----------
    wtrs_code : str
        The unique 10-digit number encoded as a string (HUC10).

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

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
    results : list of tuples
        (xtarget, ytarget, n, evp, varp)
        -- xtarget : float
               x-coordinate of target location.
        -- ytarget : float
               y-coordinate of target location.
        -- n : int
               number of neighborhood wells used in the local analysis.
        -- evp : ndarray, shape=(6, 1)
               expected value vector of the prarameters.
        -- varp : ndarray, shape=(6, 6)
               variance/covariance matrix of the parameters.

    Notes
    -----
    o   Beware! Subregion names are not unique.
    """

    # Get the watershed polygon.
    wtrs_name = getdata.get_watershed_name(wtrs_code)
    polygon = getdata.get_watershed_polygon(wtrs_code)

    # Create the associated tile string.
    if aquifers is not None:
        title_prefix = '{0} Watershed {1}: '.format(wtrs_name, aquifers)
    else:
        title_prefix = '{0} Watershed [All]: '.format(wtrs_name)

    # Carry out the Akeyaa analisis.
    results = by_polygon(polygon, aquifers, radius, reqnum, spacing, method)

    # If requested, save the run to a compressed pickle file.
    if pklzfile is not None:
        archive = {
            'aquifers': aquifers,
            'wtrs_code': wtrs_code,
            'wtrs_name': wtrs_name,
            'radius': radius,
            'reqnum': reqnum,
            'spacing': spacing,
            'method': method,
            'title_prefix': title_prefix,
            'polygon': polygon,
            'results': results
            }
        with bz2.open(pklzfile, 'wb') as fileobject:
            pickle.dump(archive, fileobject)

    return results


# -----------------------------------------------------------------------------
def by_subregion(subr_code, aquifers, radius, reqnum, spacing, method,
                 pklzfile=None):
    """
    Compute the full Akeyaa analysis across the specified hydrologic subregion.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified subregion. The grid is defined by <spacing>. The
    analysis is carried out using the wells in the specified aquifer(s) only.
    The analysis may use wells in neighboring subregions.

    Parameters
    ----------
    subr_code : str
        The unique 10-digit number encoded as a string (HUC8).

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

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
    results : list of tuples
        (xtarget, ytarget, n, evp, varp)
        -- xtarget : float
               x-coordinate of target location.
        -- ytarget : float
               y-coordinate of target location.
        -- n : int
               number of neighborhood wells used in the local analysis.
        -- evp : ndarray, shape=(6, 1)
               expected value vector of the prarameters.
        -- varp : ndarray, shape=(6, 6)
               variance/covariance matrix of the parameters.

    Notes
    -----
    o The subregion names are NOT unique.
    """

    # Get the subregion polygon.
    subr_name = getdata.get_subregion_name(subr_code)
    polygon = getdata.get_subregion_polygon(subr_code)

    # Create the associated tile string.
    if aquifers is not None:
        title_prefix = '{0} Subregion {1}: '.format(subr_name, aquifers)
    else:
        title_prefix = '{0} Subregion [All]: '.format(subr_name)

    # Carry out the Akeyaa analisis.
    results = by_polygon(polygon, aquifers, radius, reqnum, spacing, method)

    # If requested, save the run to a compressed pickle file.
    if pklzfile is not None:
        archive = {
            'aquifers': aquifers,
            'subr_name': subr_name,
            'subr_code': subr_code,
            'radius': radius,
            'reqnum': reqnum,
            'spacing': spacing,
            'method': method,
            'title_prefix': title_prefix,
            'polygon': polygon,
            'results': results
            }
        with bz2.open(pklzfile, 'wb') as fileobject:
            pickle.dump(archive, fileobject)

    return results


# -----------------------------------------------------------------------------
def by_polygon(polygon, aquifers, radius, reqnum, spacing, method):
    """
    Compute the full Akeyaa analysis across the specified polygon.

    Compute the full Akeyaa analysis for a square grid of target locations
    across the specified polygon. The grid is defined by <spacing>. The
    analysis is carried out using the wells in the specified aquifer(s) only.
    The analysis may use wells in neighboring polygons.

    Parameters
    ----------
    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the run.

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

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
    results : list of tuples
        (xtarget, ytarget, n, evp, varp)
        -- xtarget : float
               x-coordinate of target location.
        -- ytarget : float
               y-coordinate of target location.
        -- n : int
               number of neighborhood wells used in the local analysis.
        -- evp : ndarray, shape=(6, 1)
               expected value vector of the prarameters.
        -- varp : ndarray, shape=(6, 6)
               variance/covariance matrix of the parameters.

    Notes
    -----
    o   Note, data from outside of the polygon may also used in the
        computations.
    """

    # Get the well data from all authorized wells in Minnesota that are
    # completed in one of the identified aquifers.
    welldata = getdata.get_well_data(aquifers)
    xwell = np.array([well[0][0] for well in welldata])
    ywell = np.array([well[0][1] for well in welldata])
    zwell = np.array([well[1] for well in welldata])

    tree = scipy.spatial.cKDTree(np.column_stack((xwell, ywell)))

    # Create the grid of target locations across the specified polygon.
    xmin = polygon.extent.XMin
    xmax = polygon.extent.XMax
    ymin = polygon.extent.YMin
    ymax = polygon.extent.YMax

    nx = int(np.ceil((xmax - xmin)/spacing) + 1)
    xgrd = np.linspace(xmin, xmin + (nx-1)*spacing, nx)

    ny = int(np.ceil((ymax - ymin)/spacing) + 1)
    ygrd = np.linspace(ymin, ymin + (ny-1)*spacing, ny)

    # Process every grid node as a potential target.
    results = []

    for i in range(ny):
        for j in range(nx):
            xtarget = xgrd[j]
            ytarget = ygrd[i]

            if polygon.contains(arcpy.Point(xtarget, ytarget)):
                neighbors = tree.query_ball_point([xtarget, ytarget], radius)
                count = len(neighbors)

                # Carryout the weighted least squares regression.
                if count >= reqnum:
                    xactive = xwell[neighbors] - xtarget
                    yactive = ywell[neighbors] - ytarget
                    zactive = zwell[neighbors]

                    evp, varp = fit_conic(xactive, yactive, zactive, method)
                    results.append((xtarget, ytarget, count, evp, varp))

    return results


# -----------------------------------------------------------------------------
def fit_conic(x, y, z, method='RLM'):
    """
    Fit the local conic potential model to the selected heads.

    Parameters
    ----------
    x : ndarray, shape=(N,)
        x-coordinates of observation locations [m].

    y : ndarray, shape=(N,)
        y-coordinates of observation locations [m].

    z : ndarray, shape=(N,)
        observed head values [m].

    method : str (optional)
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.
            Default = 'RLM'.

    Returns
    -------
    evp : ndarray, shape=(6,)
        The expected value vector for the model parameters.

    varp : ndarray, shape=(6, 6)
        The variance matrix for the model parameters.

    Raises
    ------
    None.

    Notes
    -----
    o   The underlying conic discharge potential model is

            z = A*x**2 + B*y**2 + C*x*y + D*x + E*y + F + noise

        where the parameters maps as: [A, B, C, D, E, F] = p[0:5].

    o   Note that most of the work is done by the statsmodels library. There
        are other fitting methods available.
    """

    # Set up the coefficient matrix.
    X = np.stack([x**2, y**2, x*y, x, y, np.ones(x.shape)], axis=1)

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
