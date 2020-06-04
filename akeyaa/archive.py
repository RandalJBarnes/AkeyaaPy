"""Tools for for archiving Akeyaa runs.

Functions
---------
saveme(venue, settings, results, pklzfile)
    Save an Akeyaa run to a compressed pickle file.

loadme(pklzfile)
    Load an Akeyaa run from a compressed pickle file created by saveme.

load_and_show_results(pklzfile):
    Load an Akeyaa run and plot the results.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
04 June 2020
"""

import bz2
from datetime import datetime
import pickle

import show


# -----------------------------------------------------------------------------
def saveme(venue, settings, results, pklzfile=None):
    """Save an Akeyaa run to a compressed pickle file.

    Save an Akeyaa run (venue, settings, results) to the specified compressed
    pickle file. The bz2 (Burrows-Wheeler) compression algorithm is used. If
    no pickle file is specified a unique filename, based on the current date
    and time, is created and used.

    Parameters
    ----------
    venue: venues.Venue (concrete subclass)
        An instance of a concrete subclass of venues.Venue, e.g. City.

    settings : dict
        A complete or partial set of akeyaa_settings.

    results : list of tuples
        (xtarget, ytarget, n, evp, varp)

    pklzfile : str, optional
        The compressed pickle filename, including the extension. The
        default is None. If None, a unique filename, based on the current
        date and time, is created and used.

    Returns
    -------
    pklzfile : str
        The compressed pickle filename used.
    """

    if pklzfile == None:
        pklzfile ='Akeyaa' + datetime.now().strftime('%Y%m%dT%H%M%S') + '.pklz'

    archive = {
        'venue' : venue,
        'settings' : settings,
        'results': results
        }
    with bz2.open(pklzfile, 'wb') as fileobject:
        pickle.dump(archive, fileobject)

    return pklzfile


# -----------------------------------------------------------------------------
def loadme(pklzfile):
    """Load an Akeyaa run from a compressed pickle file created by saveme.

    Load an Akeyaa run from the specified compressed pickle file created
    by show.saveme.

    Parameters
    ----------
    pklzfile : str, optional
        A compressed pickle filename, including the extension, which was
        created by saveme.

    Returns
    -------
    tuple : (venue, settings, results)

        venue: venues.Venue (concrete subclass)
            An instance of a concrete subclass of venues.Venue, e.g. City.

        settings : dict
            A complete or partial set of akeyaa_settings.

        results : list of tuples
            (xtarget, ytarget, n, evp, varp)
    """

    with bz2.open(pklzfile, 'rb') as fileobject:
        archive = pickle.load(fileobject)

    venue = archive['venue']
    settings = archive['settings']
    results = archive['results']

    return (venue, settings, results)


# -----------------------------------------------------------------------------
def load_and_show_results(pklzfile):
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

    venue, settings, results = loadme(pklzfile)
    show.results_by_venue(venue, results)
