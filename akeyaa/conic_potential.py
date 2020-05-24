"""
Conic potential model.

Functions
---------
fit_conic(x, y, z, sigma):
    Fit the conic potential model using weighted least squares.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
23 May 2020
"""

import numpy as np
import statsmodels.api as sm


# =============================================================================
class Error(Exception):
    """
    Local base exception.
    """

class SingularMatrixError(Error):
    """
    np.linalg.inv failed.
    """

class UnknownMethodError(Error):
    """
    The requested method is not supported.
    """


#------------------------------------------------------------------------------
def ols_fit_conic(x, y, z, sigma):
    """
    Fit the conic potential model using weighted least squares.

    Arguments
    ---------
    x : ndarray, shape=(N, )
        x-coordinates of observation locations [m].

    y : ndarray, shape=(N, )
        y-coordinates of observation locations [m].

    z : ndarray, shape=(N, )
        observed head values [m].

    Returns
    -------
    evp : ndarray, shape=(6, )
        The expected value vector for the model parameters.

    varp : ndarray, shape=(6, 6)
        The variance matrix for the model parameters.

    Raises
    ------
    SingularMatrixError

    Notes
    -----
    o   The underlying model is
            z = p[0]*x**2 + p[1]*y**2 + p[2]*x*y + p[3]*x + p[4]*y + p[5] + e

    o   The variable names in this function follow the naming convention in the
        associated white paper, and not with Python convention.
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

    # Compute the rescaling.
    S = np.diag(1/np.max(np.abs(X), 0))

    # Set up the weight matrix.
    W = np.diag(1/sigma**2)

    # Do the linear algebra.
    Y = X @ S
    A = Y.T @ W @ Y

    try:
        Ainv = np.linalg.inv(A)
    except:
        raise SingularMatrixError

    evp = S @ Ainv @ Y.T @ W @ z
    varp = S @ Ainv @ S

    return (evp, varp)


#------------------------------------------------------------------------------
def fit_conic(x, y, z, method):
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

    method : str
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.

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
        ols_model = sm.OLS(z, X, M=sm.robust.norms.TukeyBiweight())
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
