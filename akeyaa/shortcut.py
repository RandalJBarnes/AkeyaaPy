"""
Akeyaa analyses functions.

Functions
---------
shortcut(what, aquifers=None, radius=3000, reqnum=25, spacing=1000,
              method='RLM', pklzfile=None):
    A shortcut way to run Akeyaa analysis and visualization with mostly
    default parameters.




by_city(code, aquifers, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified city.

by_township(code, aquifers, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified township.

by_county(code, aquifers, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified county.

by_watershed(aquifers, code, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified watershed.

by_subregion(code, aquifers, radius, reqnum, spacing, method, pklzfile)
    Compute the full Akeyaa analysis across the specified subregion.

by_polygon(aquifers, polygon, radius, reqnum, spacing, method):
    Compute the full Akeyaa analysis across the specified polygon.


fit_conic(x, y, z, method)
    Fit the conic potential model using requested method.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
27 May 2020

"""


import bz2
import pickle
import time
import numpy as np
import scipy
import statsmodels.api as sm
import arcpy

import getdata
import visualize


# -----------------------------------------------------------------------------
class Error(Exception):
    """
    Local base exception.
    """


class UnknownMethodError(Error):
    """
    The requested method is not supported.
    """


# -----------------------------------------------------------------------------
def shortcut(what, aquifers=None, radius=3000, reqnum=25, spacing=1000,
             method='RLM', pklzfile=None):
    """
    A shortcut to run Akeyaa analysis and visualization.

    The selection parameter, 'what', can be a city/township code (GNIS_ID),
    a county abbreviation (CTY_ABBR), a watershed code (HUC10), or a
    hydrologic subregion code (HUC8). This function gets the appropriate
    polygon (city, township, county, watershed, or subregion), and calls
    appropriate version of the Akeyaa engine (by_city_township, by_county,
    by_watershed, or by_subregion), and calls show_results.

    Parameters
    ----------
    what : str
        CITY:
        code : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

        TOWNSHIP:
        code : str
        The unique 8-digit Geographic Names Information System (GNIS)
        identification number encoded as a string.

        COUNTY:
        code : int
        The unique 5-digit Federal Information Processing Standards code
        (FIPS), without the initial 2 digits state code.

        WATERSHED:
        code : str
        The unique 10-digit identification number (HUC10) encoded as a string.

        SUBREGION:
        code : str
        The unique 8-digit identification number (HUC10) encoded as a string.

    aquifers : list, optional
        List of four-character aquifer abbreviation strings, as defined in
        Minnesota Geologic Survey's coding system. The default is None. If
        None, then all aquifers present will be included.

    radius : float (optional)
        Search radius for neighboring wells. radius > 0. Default = 3000 [m].

    reqnum : int (optional)
        Required number of neighboring wells. If fewer are found, the target
        location is skipped. reqnum > 6. Default = 25.

    spacing : float (optional)
        Grid spacing for target locations across the county. spacing > 0.
        Default = 1000 [m].

    method : str (optional)
        The fitting method. The currently supported methods are:
            -- 'OLS' ordinary least squares regression.
            -- 'RLM' robust linear model regression with Tukey biweights.
        Default = 'RLM'.

    pklzfile : str (optional)
        Compressed pickle file path/name. If None, the output file is not
        created. Default = None.

    Returns
    -------
    None

    Notes
    -----
    o   I am not certain that the GNIS_ID and HUC8 are non-overlapping sets.
    """

    # Initialize the stopwatch.
    start = time.time()

    # Is 'what' a code (GNIS ID)?
    try:
        _ = getdata.get_city_township_name_and_type(what)
        title_prefix, polygon, results = by_city_township(
                what, aquifers,
                radius, reqnum, spacing, method,
                pklzfile)

        visualize.show_results(title_prefix, polygon, results)
        print('Analyze {0}'.format(title_prefix))
        print('Elapsed time = {0:.4f} seconds'.format(time.time() - start))
        return

    except getdata.NotFoundError:
        pass


    # Is 'what' a cty_abbr?
    try:
        _ = getdata.get_county_name(what)
        title_prefix, polygon, results = by_county(
                what, aquifers,
                radius, reqnum, spacing, method,
                pklzfile)

        visualize.show_results(title_prefix, polygon, results)
        print('Analyze {0}'.format(title_prefix))
        print('Elapsed time = {0:.4f} seconds'.format(time.time() - start))
        return

    except getdata.NotFoundError:
        pass

    # Is 'what' a watershed code (HUC8)?
    try:
        _ = getdata.get_watershed_name(what)
        title_prefix, polygon, results = by_watershed(
                what, aquifers,
                radius, reqnum, spacing, method,
                pklzfile)

        visualize.show_results(title_prefix, polygon, results)
        print('Analyze {0}'.format(title_prefix))
        print('Elapsed time = {0:.4f} seconds'.format(time.time() - start))
        return

    except getdata.NotFoundError:
        pass

    # Is 'what' a subregion code (HUC10)?
    try:
        _ = getdata.get_subregion_name(what)
        title_prefix, polygon, results = by_subregion(
                what, aquifers,
                radius, reqnum, spacing, method,
                pklzfile)

        visualize.show_results(title_prefix, polygon, results)
        print('Analyze {0}'.format(title_prefix))
        print('Elapsed time = {0:.4f} seconds'.format(time.time() - start))
        return

    except getdata.NotFoundError:
        pass

    # Apparently, 'what' is unknown...
    raise getdata.NotFoundError(
            '"{0}" is not a valid 4-character county abbreviation, a valid '
            '10-character watershed code, or a valid 8-character hydrologic '
            'subregion code.'.format(what)
            )



