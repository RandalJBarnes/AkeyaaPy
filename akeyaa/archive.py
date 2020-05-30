import bz2
from datetime import datetime
import pickle

import show


# -----------------------------------------------------------------------------
def saveme(venue, settings, results, pklzfile=None):

    if pklzfile == None:
        pklzfile ='Gimiwan' + datetime.now().strftime('%Y%m%dT%H%M%S') + '.pklz'

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

    with bz2.open(pklzfile, 'rb') as fileobject:
        archive = pickle.load(fileobject)

    venue = archive['venue']
    settings = archive['settings']
    results = archive['results']

    return (venue, settings, results)


# -----------------------------------------------------------------------------
def load_and_show_results(pklzfile):
    """
    Load the run from a .pklz file and plot the results.

    Parameters
    ----------
    pklzfile : str
        Compressed pickle file path/name for the run.

    Returns
    -------
    None
    """

    venue, settings, results = loadme(pklzfile)
    show._by_venue(venue, results)
