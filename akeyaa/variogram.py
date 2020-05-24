import numpy as np
from scipy import spatial
import progressbar


#------------------------------------------------------------------------------
def compute_variogram(x, y, z, hmax, nh, nmin):
    """
    Compute the omni-directional experiement semi-variogram.

    Arguments
    ---------
    x : ndarray, shape=(n,)
        x coordinates.

    y : ndarray, shape=(n,)
        y coordinates.

    z : ndarray, shape=(n,)
        observed values.

    hmax : float
        maximum separation distance on the variogram plot.

    nh : int
        number of subdivisions in the variogram plot.

    nmin : int
        minimum number of pairs in a bin to be used.

    Returns
    -------
    (separ, gamma, count) : tuple
        separ : ndarray, shape=(nh, 1)
            matrix of average separation distances.

        gamma : ndarray, shape=(nh, 1)
            matrix of average semi-variogram values.

        count : ndarray, shape=(nh, 1)
            maxtrix of bin counts.

    Author
    ------
    Dr. Randal J. Barnes
    Department of Civil, Environmental, and Geo- Engineering
    University of Minnesota

    Version
    -------
    22 May 2020
    """
    # Build the KD Tree
    tree = spatial.cKDTree(np.stack((x, y), 1))

    # Initialize.
    separ = np.zeros(shape=(nh,), dtype=float)
    gamma = np.zeros(shape=(nh,), dtype=float)
    count = np.zeros(shape=(nh,), dtype=int)

    # Initialize the progress bar.
    bar = progressbar.ProgressBar(max_value=len(x))
    bar.update(0)

    # Compute the cloud of points.
    for i in range(len(x)):
        xtarget = x[i]
        ytarget = y[i]

        # This approach double counts, but this search is so much faster.
        neighbors = tree.query_ball_point([xtarget, ytarget], hmax)
        neighbors.remove(i)

        for j in neighbors:
            h = np.hypot(x[j]-xtarget, y[j]-ytarget)
            g = (z[j]-z[i])**2

            k = int(np.floor(h/hmax * nh))
            if k < nh:
                separ[k] += h
                gamma[k] += g
                count[k] += 1

        # Update the progress bar.
        bar.update(i+1)

    # Compute the averages
    for k in range(nh):
        if count[k] >= 2*nmin:
            separ[k] = separ[k]/count[k]
            gamma[k] = 0.5*gamma[k]/count[k]
        else:
            separ[k] = np.nan
            gamma[k] = np.nan

        count[k] /= 2           # Eliminate the double counting.

    return(separ, gamma, count)
