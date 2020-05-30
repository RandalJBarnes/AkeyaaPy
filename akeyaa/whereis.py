

# -----------------------------------------------------------------------------
def whereis(obj):
    """
    Plots the objects polygon over the state.

    The selection, 'obj', can be a city/county code, a county abbreviation,
    a watershed code, or a subregion code. This function gets the appropriate
    polygon (city, township, county, watershed, or subregion), and calls
    show_polygon_in_state.

    Parameters
    ----------
    obj : str
        -- an 8-digit GNIS number encoded as a string (GNIS_ID),
        -- a 4-character county abbreviation string,
        -- a 10-digit watershed number encoded as a string (HUC10), or
        -- an 8-digit subregion number encoded as a string (HUC8).

    Returns
    -------
    None
    """

    # Is 'obj' a ctu_code (GNIS ID)?
    try:
        ctu_name, ctu_type = getdata.get_city_township_name_and_type(obj)
        if ctu_type == 'CITY':
            title_str = 'City of {0}'.format(ctu_name)
        elif ctu_type == 'TOWNSHIP':
            title_str = '{0} Township'.format(ctu_name)
        else:
            title_str = '{0}'.format(ctu_name)
        polygon = getdata.get_city_township_polygon(obj)
        show_polygon_in_state(title_str, polygon)
        return

    except getdata.NotFoundError:
        pass

    # Is 'obj' is a cty_abbr?
    try:
        name = getdata.get_county_name(obj)
        title_str = '{} County'.format(name)
        polygon = getdata.get_county_polygon(obj)
        show_polygon_in_state(title_str, polygon)
        return

    except getdata.NotFoundError:
        pass

    # Is 'obj' is a watershed code?
    try:
        name = getdata.get_watershed_name(obj)
        title_str = '{} Watershed'.format(name)
        polygon = getdata.get_watershed_polygon(obj)
        show_polygon_in_state(title_str, polygon)
        return

    except getdata.NotFoundError:
        pass

    # Is 'obj' is a subregion code?
    try:
        name = getdata.get_subregion_name(obj)
        title_str = '{} Hydrologic Subregion'.format(name)
        polygon = getdata.get_subregion_polygon(obj)
        show_polygon_in_state(title_str, polygon)
        return

    except getdata.NotFoundError:
        pass

    # Apparently, 'obj' is unknown...
    raise getdata.NotFoundError(
            '"{0}" is not a valid 4-character county abbreviation, a valid '
            '10-character watershed code, or a valid 8-character hydrologic '
            'subregion code.'.format(obj)
            )








# -----------------------------------------------------------------------------
def get_state_polygon():
    """
    Get the Minnesota state boundary polygon.

    Parameters
    ----------
    None

    Returns
    -------
    polygon : arcpy.Polygon
        The state boundary polygon.

    Notes
    -----
    o   Coordinates are in 'NAD 83 UTM 15N'(EPSG:26915).
    """

    attributes = ['SHAPE@']

    with arcpy.da.SearchCursor(MNBDRY, attributes) as cursor:
        try:
            return cursor.next()[0]
        except StopIteration:
            raise NotFoundError



# -----------------------------------------------------------------------------
def show_polygon_in_state(title_str, polygon):
    """
    Plot the polygon over the state.

    Plot the polygon as a blue-filled shape overlying Minnesota, which is
    plotted as a grey-filled shape.

    Parameters
    ----------
    title_str : str
        The plot title.

    polygon : arcpy.Polygon
        https://pro.arcgis.com/en/pro-app/arcpy/classes/polygon.htm
        The geographic focus of the run.

    Returns
    -------
    None
    """

    # Get the polygon boundary information.
    xpoly = [pnt.X for pnt in polygon.getPart(0)]
    ypoly = [pnt.Y for pnt in polygon.getPart(0)]

    # Get the state boundary information.
    state = getdata.get_state_polygon()
    xstate = [pnt.X for pnt in state.getPart(0)]
    ystate = [pnt.Y for pnt in state.getPart(0)]

    # Plot the well locations coded by aquifer.
    plt.figure()
    plt.axis('equal')

    plt.fill(xstate, ystate, '0.90')
    plt.fill(xpoly, ypoly, 'b')

    plt.xlabel('Easting [m]')
    plt.ylabel('Northing [m]')
    plt.title(title_str, {'fontsize': 24})
    plt.grid(True)
# -*- coding: utf-8 -*-
