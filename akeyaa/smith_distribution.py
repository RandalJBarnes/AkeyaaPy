"""
Functions for the care and feeding of Smith's distribution.

Functions
---------
smith_pdf(alpha, mu, sigma):
    Evaluate the probability density function for Smith's distribution.

smith_cdf(alpha, mu, sigma):
    Evaluate the cumulative distribution function for Smith's distribution.

smith_quartiles(mu, sigma):
    Returns the nominal quartile of Smith's distribution.

Notes
-----
o   Smith's distribution is a 2D circular distribution.  The domain is
    [0, 2pi].

o   The variance/covariance matrix, sigma, must be positive definite.

o   Smith's distribution is the distribution of for the direction of a
    random vector in 2D with independent, Normally distributed, components.

o   Smith's distribution is also called the "General Projected Normal
    distribution". See, for example, Lark et a. [2014] or Hernandez-
    Stumpfhauser [2017].

o   See Justus [1978, Equation (4-11)] or Carta et al. [2008, Equation (6)]
    for details on the Smith's distribution pdf.

o   The variable names in this function follow the naming convention in the
    associated white paper, and not with Python convention.

References
----------
o   J. A. Carta, C. Bueno, and P. Ramirez. Statistical modeling of
    directional wind speeds using mixture of von mises distribution:
    Case study. Energy Conversion and Management, 49:897-907, 2008.

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
18 May 2020
"""

from math import pi, cos, sin, exp, sqrt, atan2
import numpy as np
from scipy.linalg import inv, det
from scipy.stats import norm
from scipy.integrate import quad
from scipy.optimize import fsolve


#------------------------------------------------------------------------------
def smith_pdf(alpha, mu, sigma):
    """
    Evaluate the probability density function for Smith's distribution.

    Evaluate the probability density function for Smith's distribution at the
    angles given in the array 'alpha' using the component mean vector `mu` and
    the component variance matrix `sigma`.

    Parameters
    ----------
    alpha : ndarray, shape(M, ); or list; or scalar.
        The angles at which to evaluate the pdf. The angles are given in
        radians, not degrees.

    mu : ndarray, shape(2,1)
        The component mean vector.

    sigma : ndarray, shape(2,2)
        The compontnet variance matrix.

    Returns
    -------
    pdf : ndarray, shape (M, )
        The array of pdf values at each of the angles specified in `alpha`.

    Raises
    ------
    None
    """

    # Preallocate space.
    if isinstance(alpha, np.ndarray):
        pdf = np.empty(alpha.shape[0])
    elif isinstance(alpha, list):
        pdf = np.empty(len(alpha))
    else:
        alpha = [alpha]
        pdf = np.empty([1,])

    # Precompute what can be precomputed.
    sigma_inv = inv(sigma)
    det_sigma_inv = det(sigma_inv)

    A = sqrt(det_sigma_inv)/(2*pi);
    D = mu.T @ sigma_inv @ mu

    # Fill the pdf for all angles.
    for j, a in enumerate(alpha):
        r = np.array([[cos(a)], [sin(a)]])
        B = r.T @ sigma_inv @ r
        C = r.T @ sigma_inv @ mu / sqrt(B)
        pdf[j]= A/B * (exp(-D/2) + C*sqrt(2*pi) * exp((C**2 - D)/2) * norm.cdf(C, 0, 1))

    return pdf


#------------------------------------------------------------------------------
def smith_cdf(lb, ub, mu, sigma):
    """
    Evaluate the Pr(lb < alpha < ub) for Smith's distribution.

    Evaluate the Pr(lb < alpha < ub) for Smith's distribution using the
    component mean vector `mu` and the component variance matrix `sigma`.

    Since Smith's distrubiot is a circular distribution
        Pr(lb < alpha < ub) + Pr(ub < alpha < 2pi + lb) = 1

    Parameters
    ----------
    lb : float
        lower bound on the angular range. lb < ub.

    ub : float
        upper bound on the angular range. ub > lb.

    mu : ndarray, shape(2,1)
        The component mean vector.

    sigma : ndarray, shape(2,2)
        The compontnet variance matrix.

    Returns
    -------
    cdf : float
        Pr(lb < alpha < ub)

    Raises
    ------
    None
    """

    cdf = quad(lambda alpha : smith_pdf(alpha, mu, sigma), lb, ub)[0]
    return cdf


#-------------------------------------------------------------------------------
def smith_quartiles(mu, sigma):
    """
    Returns the nominal quartile of Smith's distribution.

    Returns the angular median (mean) and nominal angular quartiles of the
    Smith's distribution with component mean vector mu and component variance
    matrix sigma.

    Arguments
    ---------
    mu : ndarray, shape(2,1)
        The component mean vector.

    sigma : ndarray, shape(2,2)
        The compontnet variance matrix.

    Returns
    -------
    a25 : [radians] angle defined by two conditions
            -- a25 < a50 and
            -- Pr(a25 < alpha < a50) = 0.25

    a50 : [radians] mean angle

    a75 : [radians] angle defined by two conditions
            -- a75 > a50 and
            -- Pr(a50 < alpha < a75) = 0.25

    Notes
    -----
    o   Since Simth's distribution is circular, the concept of percentiles
        are ambiguous. Note the definitions given above.

    o   It is possible for a25 to be less that 0.

    o   It is possible for a75 to be greater than 2pi.
    """
    a50 = atan2(mu[1], mu[0])
    a75 = fsolve(lambda ub : quad(lambda alpha : smith_pdf(alpha, mu, sigma),
                                  a50, ub)[0]-0.25, a50+pi/10)
    a25 = fsolve(lambda lb : quad(lambda alpha : smith_pdf(alpha, mu, sigma),
                                  lb, a50)[0]-0.25, a50-pi/10)

    return (a25[0], a50, a75[0])