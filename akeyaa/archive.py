"""Save and load complete Akeyaa runs from compressed pickle files."""
import bz2
from datetime import datetime
import pickle


# -----------------------------------------------------------------------------
def saveme(venue, settings, results, pklzfile=None):
    """Save an Akeyaa run to a compressed pickle file.

    Save an Akeyaa run to the specified compressed pickle file `pklzfile`.
    If no pickle file is specified, a unique filename, based on the current
    date and time, is created and used.

    Parameters
    ----------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated in `akeyaa.venues`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    settings : type
        Validated akeyaa parameters, as enumerated in `akeyaa.parameters`.

    results : list[tuple]
        The tuples are of the form (xtarget, ytarget, n, evp, varp), as
        detailed in 'akeyaa.analyze'.

    pklzfile : str, optional
        The compressed pickle filename, including the extension. The
        default is None. If None, a unique filename, based on the current
        date and time, is created and used.

    Returns
    -------
    pklzfile : str
        The compressed pickle filename used.

    See Also
    --------
    akeyaa.analyze, akeyaa.parameters, akeyaa.venues

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
    pklzfile : str
        A compressed pickle filename, including the extension, which was
        created by saveme.

    Returns
    -------
    venue: type
        An instance of a political division, administrative region, or
        user-defined domain, as enumerated in `akeyaa.venues`.
        For example: a ``City``, ``Watershed``, or ``Neighborhood``.

    settings : type
        Validated akeyaa parameters, as enumerated in `akeyaa.parameters`.

    results : list[tuple]
        The tuples are of the form (xtarget, ytarget, n, evp, varp), as
        detailed in `akeyaa.analyze`.

    See Also
    --------
    akeyaa.analyze, akeyaa.parameters, akeyaa.venues

    """
    with bz2.open(pklzfile, "rb") as fileobject:
        archive = pickle.load(fileobject)

    venue = archive["venue"]
    settings = archive["settings"]
    results = archive["results"]

    return (venue, settings, results)
