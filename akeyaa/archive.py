"""Tools for for archiving Akeyaa runs.

Functions
---------
saveme(venue, settings, results, pklzfile)
    Save an Akeyaa run to the compressed pickle file.

loadme(pklzfile)
    Load an Akeyaa run from a compressed pickle file created by saveme.

load_and_show(pklzfile):
    Load an Akeyaa run and plot the results.

"""
import bz2
from datetime import datetime
import pickle

import show


# -----------------------------------------------------------------------------
def saveme(venue, settings, results, pklzfile=None):
    """Save an Akeyaa run to a compressed pickle file.

    Save an Akeyaa run (`venue`, `settings`, `results`) to the specified
    compressed pickle file `pklzfile`. If no pickle file is specified, a
    unique filename, based on the current date and time, is created and used.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in venues.py.
        For example: a 'City', 'Watershed', or 'Neighborhood'.

    settings : type
        A complete, validated set of akeyaa parameters, as enumerated and
        detailed in parameters.py.

    results : list[tuples]
        (xtarget, ytarget, n, evp, varp)

    pklzfile : str, optional
        The compressed pickle filename, including the extension. The
        default is None. If None, a unique filename, based on the current
        date and time, is created and used.

    Returns
    -------
    pklzfile : str
        The compressed pickle filename used.

    Notes
    -----
    The bz2 (Burrows-Wheeler) compression algorithm is used.

    """
    if pklzfile is None:
        pklzfile = "Akeyaa" + datetime.now().strftime("%Y%m%dT%H%M%S") + ".pklz"

    archive = {"venue": venue, "settings": settings, "results": results}
    with bz2.open(pklzfile, "wb") as fileobject:
        pickle.dump(archive, fileobject)

    return pklzfile


# -----------------------------------------------------------------------------
def loadme(pklzfile):
    """Load an Akeyaa run from a compressed pickle file created by saveme.

    Parameters
    ----------
    pklzfile : str, optional
        A compressed pickle filename, including the extension, which was
        created by saveme.

    Returns
    -------
    venue : type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated and detailed in venues.py.
        For example: a 'City', 'Watershed', or 'Neighborhood'.

    settings : type
        A complete, validated set of akeyaa parameters, as enumerated and
        detailed in parameters.py.

    results : list[tuples]
        (xtarget, ytarget, n, evp, varp)

    """
    with bz2.open(pklzfile, "rb") as fileobject:
        archive = pickle.load(fileobject)

    venue = archive["venue"]
    settings = archive["settings"]
    results = archive["results"]

    return (venue, settings, results)


# -----------------------------------------------------------------------------
def load_and_show(pklzfile):
    """Load an Akeyaa run and plot the results.

    Load an Akeyaa run from the specified compressed pickle file created
    by show.saveme and plot the results using show.by_venue.

    Parameters
    ----------
    pklzfile : str
        A compressed pickle filename, including the extension, which was
        created by show.saveme.

    Returns
    -------
    None

    """
    venue, _, results = loadme(pklzfile)
    show.by_venue(venue, results)
