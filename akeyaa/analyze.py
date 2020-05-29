import bz2
import pickle
import numpy as np
import statsmodels.api as sm

import arcpy

import venue
import wells


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
def by_venue(, aquifers, database, radius, reqnum, spacing, method, pklzfile=None):

    # Get the polygon.
    polygon = getdata.get_city_polygon(code)

    # Create the associated title prefix string.
    name = getdata.get_city_name(code)

    if aquifers is not None:
        prefix = 'City of {0} {1}: '.format(name, aquifers)
    else:
        prefix = 'City of {0} [All]: '.format(name)

    # Carry out the Akeyaa analisis.
    results = by_polygon(polygon, aquifers, radius, reqnum, spacing, method)

    # If requested, save the run to a compressed pickle file.
    if pklzfile is not None:
        archive = {
            'aquifers': aquifers,
            'code': code,
            'name': name,
            'radius': radius,
            'reqnum': reqnum,
            'spacing': spacing,
            'method': method,
            'prefix': prefix,
            'polygon': polygon,
            'results': results
            }
        with bz2.open(pklzfile, 'wb') as fileobject:
            pickle.dump(archive, fileobject)

    return (prefix, polygon, results)


# -----------------------------------------------------------------------------
def by_polygon(polygon, aquifers, database, radius, reqnum, spacing, method):
    """
    """

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
            xo = xgrd[j]
            yo = ygrd[i]

            if polygon.contains(arcpy.Point(xo, yo)):
                xw, yw, zw = database.fetch([xo, yo], radius, aquifers)

                # Carryout the weighted least squares regression.
                # Note that we are converting the z in [ft] to [m].
                if len(xw) >= reqnum:
                    evp, varp = fit_conic(xw-xo, yw-yo, 0.3048*zw, method)
                    results.append((xo, yo, len(xw), evp, varp))

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

        where the parameters map as: [A, B, C, D, E, F] = p[0:5].

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
