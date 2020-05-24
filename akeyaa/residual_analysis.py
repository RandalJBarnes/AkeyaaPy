"""
Residual analyses functions.

Functions
---------

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
23 May 2020
"""

import bz2
import matplotlib.pyplot as plt
import pickle
import progressbar
import numpy as np
from scipy import spatial

from conic_potential import fit_conic
from get_data import get_well_data
from variogram import compute_variogram


# -----------------------------------------------------------------------------
def compute_residuals(aquifer_list, radius, reqnum, method, residpklz=None):
    """
    """

    # Get the well data from ArcGIS.
    welldata = get_well_data(aquifer_list)

    x = np.array([row[0][0] for row in welldata])
    y = np.array([row[0][1] for row in welldata])
    z = np.array([row[1] for row in welldata])

    # Create a KD search tree.
    tree = spatial.cKDTree(np.stack((x, y), 1))

    # Initialize the progress bar.
    bar = progressbar.ProgressBar(max_value=len(welldata))
    bar.update(0)

    # Process every well location as a target.
    residuals = []

    for i in range(len(welldata)):
        xtarget = x[i]
        ytarget = y[i]
        ztarget = z[i]
        relateid = welldata[i][4]

        active_wells = tree.query_ball_point([xtarget, ytarget], radius)
        active_wells.remove(i)
        n = len(active_wells)

        # Carryout the weighted least squares regression.
        if n >= reqnum:
            xw = x[active_wells]
            yw = y[active_wells]
            zw = z[active_wells]

            evp, varp = fit_conic(xw-xtarget, yw-ytarget, zw, method)
            zest = evp[5]
            zstd = np.sqrt(varp[5, 5])
            residuals.append((xtarget, ytarget, ztarget, zest, zstd, n, relateid))

        # Update the progress bar.
        bar.update(i+1)

    # If requested, save the results to a compressed pickle file.
    if residpklz is not None:
        archive = {
            'aquifer_list' : aquifer_list,
            'radius' : radius,
            'reqnum' : reqnum,
            'mathod' : method,
            'residuals' : residuals
            }
        with bz2.open(residpklz, 'wb') as fp:
            pickle.dump(archive, fp)

    return residuals


# -----------------------------------------------------------------------------
def compute_residual_variogram(residpklz, hmax, nh, nmin, variopklz=None):
    """
    """

    # Get the residual data from the pickle file.
    with bz2.open(residpklz, 'rb') as fp:
        archive = pickle.load(fp)

    aquifer_list = archive.get('aquifer_list')
    radius = archive.get('radius')
    reqnum = archive.get('reqnum')
    method = archive.get('method')
    residuals = archive.get('residuals')

    # Unpack the data.
    x = np.array([row[0] for row in residuals])
    y = np.array([row[1] for row in residuals])
    e = np.array([row[2]-row[3] for row in residuals])

    # Compute the variogram.
    separ, gamma, count = compute_variogram(x, y, e, hmax, nh, nmin)

    # If requested, save the results to a compressed pickle file.
    if variopklz is not None:
        archive = {
            'aquifer_list' : aquifer_list,
            'radius' : radius,
            'reqnum' : reqnum,
            'method' : method,
            'residuals' : residuals,
            'hmax' : hmax,
            'nh' : nh,
            'nmin' : nmin,
            'x' : x,
            'y' : y,
            'e' : e,
            'separ' : separ,
            'gamma' : gamma,
            'count' : count
            }
        with bz2.open(variopklz, 'wb') as fp:
            pickle.dump(archive, fp)


#------------------------------------------------------------------------------
def view_residual_variogram(variopklz):
    """
    """

    # Load the data.
    with bz2.open(variopklz, 'rb') as fp:
        archive = pickle.load(fp)

    # Unpack the data.
    aquifer_list = archive.get('aquifer_list')
    hmax = archive.get('hmax')
    e = archive.get('e')
    separ = archive.get('separ')
    gamma = archive.get('gamma')
    count = archive.get('count')

    vare = np.var(e)

    # Plot the semivariogram.
    plt.figure()
    plt.plot(separ, gamma, 'o')
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.ylabel('Semi-variogram [m^2]')
    plt.xlabel('Sparation Distance [m]')
    plt.title('Residuals: {}'.format(aquifer_list))

    plt.figure()
    plt.plot(separ, count/2, 'o')
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    plt.ylabel('Number of Pairs [#]')
    plt.xlabel('Sparation Distance [m]')
    plt.title('Residuals: {}'.format(aquifer_list))


# -----------------------------------------------------------------------------
def compute_nn_statistics(aquifer_list, nnpklz=None):
    """
    """

    welldata = get_well_data(aquifer_list)

    x = np.array([row[0][0] for row in welldata])
    y = np.array([row[0][1] for row in welldata])
    z = np.array([row[1] for row in welldata])

    # Create a KD search tree.
    xy = np.stack((x, y), 1)
    tree = spatial.cKDTree(xy)

    # Compute the nearest-neighbor.
    dist = np.empty(x.shape)
    diff = np.empty(x.shape)
    indx = np.empty(x.shape, dtype=int)

    for i in range(xy.shape[0]):
        d, j = tree.query(xy[i], 2)
        if j[0] != i:
            indx[i] = j[0]
            dist[i] = d[0]
            diff[i] = z[i] - z[j[0]]
        else:
            indx[i] = j[1]
            dist[i] = d[1]
            diff[i] = z[i] - z[j[1]]

    # If requested, save the results to a compressed pickle file.
    if nnpklz is not None:
        archive = {
            'aquifer_list' : aquifer_list,
            'z' : z,
            'dist' : dist,
            'diff' : diff,
            'indx' : indx
            }
        with bz2.open(nnpklz, 'wb') as fp:
            pickle.dump(archive, fp)

    return(z, dist, diff, indx)