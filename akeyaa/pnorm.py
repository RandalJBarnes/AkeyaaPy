"""
Support for the general projected normal distribution.

Functions
---------
pnormpdf(theta, mu, sigma):
    Evaluate the probability density function for the general projected
    normal distribution.

pnormcdf(lb, ub, mu, sigma):
    Evaluate the Pr(lb < theta < ub) for a general projected normal
    distribution.

Notes
-----
o   The variance/covariance matrix, sigma, must be positive definite.

o   The general projected normal distribution is a 2D circular distribution.
    The domain is [0, 2pi]. See, for example, Lark [2014].

o   See Justus [1978, (4-11)] or Hernandez et al. [2017, (1)] for details on
    the general projected normal distribution pdf.

References
----------
o   D. Hernandez-Stumpfhauser, F. J. Breidt, and M. J. van der Woerd.
    The General Projected Normal Distribution of Arbitrary Dimension:
    Modeling and Bayesian Inference Bayesian Analysis. Institute of
    Mathematical Statistics, 12:113-133, 2017.

o   C. G. Justus. Winds and Wind System Performance. Solar energy.
    Franklin Institute Press, Philadelphia, Pennsylvania, 1978. ISBN
    9780891680062. 120 pp.

o   R. M. Lark, D. Clifford, and C. N. Waters. Modelling complex geological
    circular data with the projected normal distribution and mixtures of
    von Mises distributions. Solid Earth, Copernicus GmbH, 5:631-639, 2014.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
26 May 2020

"""

from math import cos, sin, exp, sqrt, pi
import numpy as np
from scipy.stats import norm
from scipy.integrate import quad


# -----------------------------------------------------------------------------
def pnormpdf(theta, mu, sigma):
    """
    Evaluate the probability density function for the general projected
    normal distribution.

    Parameters
    ----------
    theta : ndarray, shape(M, ); or list; or scalar.
        The angles at which to evaluate the pdf. The angles are given in
        radians, not degrees.

    mu : ndarray, shape=(2, 1)
        The mean vector.

    sigma : ndarray, shape=(2, 2)
        The variance matrix.

    Returns
    -------
    pdf : ndarray, shape (M, )
        The array of pdf values at each of the angles specified in `alpha`.

    Raises
    ------
    None

    Notes
    -----
    o   This implementation is based on (1) in Hernandez et al. [2017].
        However, the representation given by Hernandez et al. is prone to
        numerical overflow. The ameliorate the problem we have refactored
        the equation.
    """

    # Preallocate space.
    if isinstance(theta, np.ndarray):
        pdf = np.empty(theta.shape[0])
    elif isinstance(theta, list):
        pdf = np.empty(len(theta))
    else:
        theta = [theta]
        pdf = np.empty([1, ])

    # Precompute what can be precomputed.
    detS = sigma[0, 0]*sigma[1, 1] - sigma[0, 1]*sigma[1, 0]
    Sinv = np.array([[sigma[1, 1], -sigma[0, 1]],
                     [-sigma[1, 0], sigma[0, 0]]]) / detS

    C = mu.T @ Sinv @ mu
    D = 2*pi*sqrt(detS)

    # Fill the pdf for all angles.
    for j, t in enumerate(theta):
        r = np.array([[cos(t)], [sin(t)]])
        A = r.T @ Sinv @ r                  # A is always a positive number.
        B = r.T @ Sinv @ mu
        E = B/sqrt(A)
        pdf[j] = (exp(-C/2) + E*norm.cdf(E)*sqrt(2*pi*exp(E*E - C)))/(A*D)

    return pdf


# -----------------------------------------------------------------------------
def pnormcdf(lb, ub, mu, sigma):
    """
    Evaluate the Pr(lb < theta < ub) for a general projected normal
    distribution.

    Parameters
    ----------
    lb : float
        lower integration bound on the angular range. lb < ub.

    ub : float
        upper integration bound on the angular range. ub > lb.

    mu : ndarray, shape=(2, 1)
        The mean vector.

    sigma : ndarray, shape=(2, 2)
        The variance matrix.

    Returns
    -------
    cdf : float
        Pr(lb < alpha < ub)

    Raises
    ------
    None
    """

    cdf = quad(lambda theta: pnormpdf(theta, mu, sigma), lb, ub)[0]
    return cdf
