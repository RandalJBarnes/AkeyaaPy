"""



Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
12 May 2020
"""

#-------------------------------------------------------------------------------
def inakeyaa(i50, data, dst):
    """
    Compute and plot the posterior pdf for the inferred flow direction.

    Compute and plot the posterior pdf for the inferred uniform flow direction
    for a simple planar model using a Bayesian framework.

    Parameters
    ----------
    i50 : float
        median of the subjective prior distribution for the magnitude of the
        head gradient.

    data : (nx4) float array
        matrix of measured head data.
        -   The first column contains the x-coordinates,
        -   the second column contains the y-coordiantes,
        -   the third column contains the measured heads, and
        -   the fourth column contains the assoicated standard deviations.

    dst : string
        destination folder.

    Returns
    -------
    alpha : (Mx1) float array
        array of uniformly distributed angles (flow directions) from
        0 to 2*pi radians.

    f : (Mx1) float array
        posterior probability density function evaluated at the angles
        given in alpha.

    KLdiv : (Nx1) float array
        Kullback-Liebler divergence for each of the N "leave-one-out"
        analyses.

    Raises
    ------

    Notes
    -----
    o   Inakeyaa (In-a-kay-ah) is the Ojibwe word for the phrase "in that
        direction" [Weshki-ayaad et al., 2019],  which seems appropriate for
        this project.

    o   This routine automatically generates 6 plots.
        -   Plot #1 : a post plot of the data
        -   Plot #2 : posterior density (rectangular)
        -   Plot #3 : posterior density (polar)
        -   Plot #4 : "leave-one-out" Kullbach-Liebler divergence
        -   Plot #5 : "leave-one-out" posterior densities (rectangular)
        -   Plot #6 : "leave-one-out" posterior densities (polar)

    o   This routine generates an output file "inikeyaa.csv", which contains
        the results from the run.

    References
    ----------
    -   Weshki-ayaad, Charlie Lippert, and Guy T. Gambill. Freelang ojibwe-
        english and english-ojibwe online dictionary, July 2019.
        URL https://www.freelang.net/online/ojibwe.

    """
    import os

    import matplotlib
    matplotlib.use('Agg')

    import matplotlib.pyplot as plt

    from math import pi
    import numpy as np

    # Remove all of the old output files, if they exist.
    for k in range(1,7):
        fname = 'inakeyaa%02d.png' % k
        if os.access(dst+fname, os.F_OK):
            os.remove(dst+fname)

    if os.access(dst+'inakeyaa.csv', os.F_OK):
        os.remove(dst+'inakeyaa.csv')

    # Create the sweep of angles at which the pdf is evaluated.
    M = 361
    N = data.shape[0]
    alpha = np.linspace(0., 2*pi, M)
    a = np.linspace(0, 360, M)

    # Compute the posterior distribution using all of the data.
    (mu, sigma) = bayesian_regression(i50, data)
    f = smithpdf(alpha, mu, sigma)

    # Compare the pdf using all of the data, to each of the pdf's using the
    # "leave-one-out" subsets.  Compute the Kullback-Liebler divergence for
    #  each as a measure of influential data.
    g = np.zeros([M, N])
    KLdiv = np.zeros([N])

    for i in range(N):
        I = np.nonzero(np.arange(N) != i)
        (mu, sigma) = bayesian_regression(i50, data[I, :][0])  # a work around
        g[:, i] = smithpdf(alpha, mu, sigma)
        KLdiv[i] = sum( g[0:M-1, i] * np.log2( g[0:M-1, i] / f[0:M-1] ) ) * 2*pi/(M-1)

    # Plot #1 : post plot
    plt.figure()

    plt.scatter(data[:,0], data[:,1], marker='o', c='b', s=10)
    plt.axis('equal')
    for i in range(N):
        plt.text(data[i,0], data[i,1], '%.2f' % data[i,2])
    plt.xlabel('X-coordinate')
    plt.ylabel('Y-coordinate')

    plt.savefig(dst+'inakeyaa01.png')

    # Plot #2 : posterior density (Cartesian)
    plt.figure()
    plt.plot(a, f*pi/180.)

    plt.plot(a, np.ones((M,1))/360, '-r')

    plt.xlabel('Direction [deg]')
    plt.ylabel('Probability Density Function')
    L = plt.axis()
    plt.axis([0., 360., 0., L[3]])
    plt.xticks(np.linspace(0., 360., 13))
    plt.savefig(dst+'inakeyaa02.png')

    # Plot #3 : posterior density (polar)
    plt.figure()
    plt.polar(alpha, f*pi/180.)

    plt.polar(alpha, np.ones((M,1))/360, '-r')

    plt.savefig(dst+'inakeyaa03.png')

    # Plot #4 : "leave-one-out" Kullbach-Liebler divergence
    plt.figure()
    plt.plot(range(1, N+1), KLdiv, 'o')
    plt.xlabel('Observation [#]')
    plt.ylabel('KL Divergence [bits]')
    plt.savefig(dst+'inakeyaa04.png')

    # Plot #05 : "leave-one-out" posterior densities (Cartesian)
    plt.figure()

    for i in range(N):
        plt.plot(a, g[:, i]*pi/180)

    plt.xlabel('Direction [deg]')
    plt.ylabel('Probability Density Function')
    L = plt.axis()
    plt.axis([0., 360., 0., L[3]])
    plt.xticks(np.linspace(0., 360., 13))

    plt.savefig(dst+'inakeyaa05.png')

    # Plot #06 : "leave-one-out" posterior densities (polar)
    plt.figure()
    for i in range(N):
        plt.polar(alpha, g[:, i]*pi/180.)

    plt.savefig(dst+'inakeyaa06.png')

    # Create the .csv file
    outfile = open(dst+'inakeyaa.csv', 'w')

    outfile.write('"i50"\n')
    outfile.write('%g\n' % i50)

    outfile.write('"x","y","head","stdev","KLdiv"\n')
    for i in range(N):
        outfile.write('%g, %g, %g, %g, %g\n' % (data[i,0], data[i,1], data[i,2], data[i,3], KLdiv[i]))

    outfile.write('"alpha","pdf"\n')
    for j in range(M):
        outfile.write('%g, %g\n' % (alpha[j], f[j]))

    outfile.close()

    return (alpha, f, KLdiv)


#-------------------------------------------------------------------------------
def bayesian_regression(i50, data):
    """
    Compute the Bayesian regression for Inakeyaa.

    Compute the posterior mean and variance for a specialized Bayesian
    regression of a simple plane:  z = ax + by + c.

    Parameters
    ----------
    i50 : float
        median of the subjective prior distribution for the magnitude of the
        head gradient.

    data : (nx4) float array
        matrix of measured head data.
        -   The first column contains the x-coordinates,
        -   the second column contains the y-coordiantes,
        -   the third column contains the measured heads, and
        -   the fourth column contains the assoicated standard deviations.

    Returns
    -------
    (mu, sigma) : tuple

    mu : (2x1) float array
        The mean vector for the random vector's components.

    sigma : (2x2) float array
        The variance/covariance matrix for the random vector's components.

    Raises
    ------

    Notes
    -----
    -   See Wang [2009, Section 2.2] or Reis et al. [2005] for details on the
        derivation.

    -   If the H matrix is signular, return the wholly uninformed prior as the
        posterior.

    References
    ----------
    -  D. S. Reis, J. R. Stedinger, and E. S. Martins. Bayesian generalized
       least squares regression with application to log Pearson type 3 regional
       skew estimation. Water Resources Research, 41(W10419), 2005.
       doi:10.1029/2004WR003445.

    -  Zhen Wang. Semi-parametric Bayesian Models Extending Weighted Least
       Squares. PhD thesis, Ohio State University, 2009.

    """

    from math import log, sqrt
    import numpy as np

    N = data.shape[0]

    X = np.hstack((data[:, 0:2] - np.median(data, 0)[0:2], np.ones((N, 1))))
    z = data[:,2]

    Ginv = np.diag(1./data[:,3]**2)

    v = (i50 / sqrt(2*log(2)))**2
    Vinv = np.array([[1/v, 0, 0], [0, 1/v, 0], [0, 0, 0]])
    H = Vinv + np.dot(np.dot(X.T, Ginv), X)

    try:
        Vwz = np.linalg.inv(H)
    except:
        mu = np.zeros((2,1))
        sigma = np.eye(2)
    else:
        Ewz = np.dot(Vwz, np.dot(np.dot(X.T, Ginv), z))
        mu = Ewz[0:2]
        sigma = Vwz[0:2, 0:2]

    return(mu, sigma)


#-------------------------------------------------------------------------------
def smithpdf(alpha, mu, sigma):
    """
    Evaluate the probability density function for Smith's distribution.

    Evaluate the probability density function for Smith's distribution at the
    angles given in the array `alpha` using the component mean vector `u` and
    the component variance/covariance matrix `S`.

    Parameters
    ----------
    alpha : (mx1) float array
        An array of angles at which to evaluate the pdf. The angles are given
        in radians, not degrees.

    mu : (2x1) float array
        The mean vector for the random vector's components.

    sigma : (2x2) float array
        The variance/covariance matrix for the random vector's components.

    Returns
    -------
    pdf : (mx1) float array
        The array of pdf values at each of the angles specified in `alpha`.

    Raises
    ------

    Notes
    -----
    -   Smith's distribution is a 2D circular distribution.  The domain is
        [0, 2pi].

    -   The variance/covariance matrix, S, must be positive definite.

    -   Smith's distribution is the distribution of for the direction of a
        random vector in 2D with independent, Normally distributed, components.

    -   See Justus [1978, Equation (4-11)] or Carta et al. [2008, Equation (6)]
        for details on the Smith's distribution pdf.

    References
    ----------
    -   J. A. Carta, C. Bueno, and P. Ramirez. Statistical modeling of
        directional wind speeds using mixture of von mises distribution:
        Case study. Energy Conversion and Management, 49:897-907, 2008.

    -   C. G. Justus. Winds and Wind System Performance. Solar energy.
        Franklin Institute Press, Philadelphia, Pennsylvania, 1978. ISBN
        9780891680062. 120 pp.
    """

    from math  import pi, cos, sin, exp, sqrt
    import numpy as np
    from scipy import stats

    # Validate the arguments

    # sigma must be positive definite.
    det_sigma = sigma[0, 0]*sigma[1, 1] - sigma[0, 1]*sigma[1, 0]
    assert( (sigma[0, 0] > 0.) & (sigma[1, 1] > 0.) & (det_sigma > 0.) )

    # All alpha must be in the domain [0, 2pi].
    assert( (min(alpha) >= 0.) & (max(alpha) <= 2.*pi) )

    # Fill pdf
    A = 1 / (2*pi* sqrt(det_sigma))
    D = (mu[0]*sigma[1, 1]*mu[0] - 2*mu[0]*sigma[0, 1]*mu[1] + mu[1]*sigma[0, 0]*mu[1]) / det_sigma

    pdf = np.zeros( [len(alpha)] )
    for j in range( len(alpha) ):
        r = [ cos(alpha[j]), sin(alpha[j]) ]
        B = (r[0]*sigma[1, 1]* r[0] - r[0]*sigma[1, 0]* r[1] - r[1]*sigma[0, 1]* r[0] + r[1]*sigma[0, 0]* r[1]) / det_sigma
        C = (r[0]*sigma[1, 1]*mu[0] - r[0]*sigma[1, 0]*mu[1] - r[1]*sigma[0, 1]*mu[0] + r[1]*sigma[0, 0]*mu[1]) / (det_sigma * sqrt(B))
        pdf[j] = A/B * (1 + C * sqrt(2*pi) * exp(C**2 / 2) * stats.norm.cdf(C, 0, 1)) * exp(-D/2)

    return pdf


#-------------------------------------------------------------------------------
def mydump(data, Vinv, Ginv, X, H):
    """
    Dump a few matrices out for debugging the cgi.
    """

    import time

    outfile = open('mydump.log', 'a')
    outfile.write('\n\n'+time.asctime()+'\n')

    outfile.write('data(%d x %d)\n' % (data.shape[0], data.shape[1]))
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            outfile.write('%g ' % data[i,j])
        outfile.write('\n')
    outfile.write('\n')

    outfile.write('Vinv(%d x %d)\n' % (Vinv.shape[0], Vinv.shape[1]))
    for i in range(Vinv.shape[0]):
        for j in range(Vinv.shape[1]):
            outfile.write('%g ' % Vinv[i,j])
        outfile.write('\n')
    outfile.write('\n')

    outfile.write('Ginv(%d x %d)\n' % (Ginv.shape[0], Ginv.shape[1]))
    for i in range(Ginv.shape[0]):
        for j in range(Ginv.shape[1]):
            outfile.write('%g ' % Ginv[i,j])
        outfile.write('\n')
    outfile.write('\n')

    outfile.write('X(%d x %d)\n' % (X.shape[0], X.shape[1]))
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            outfile.write('%g ' % X[i,j])
        outfile.write('\n')
    outfile.write('\n')

    outfile.write('H(%d x %d)\n' % (H.shape[0], H.shape[1]))
    outfile.write('%g %g %g\n' % (H[0,0], H[0,1], H[0,2]))
    outfile.write('%g %g %g\n' % (H[1,0], H[1,1], H[1,2]))
    outfile.write('%g %g %g\n' % (H[2,0], H[2,1], H[2,2]))
    outfile.write('\n')

    outfile.close()