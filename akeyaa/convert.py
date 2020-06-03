"""Convert coordinates.

Functions
---------
convert_polygon(polygon)
    Convert a polygon's coordinates from lat/lon to UTM.


Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
02 June 2020

"""

import arcpy
import pyproj


# -----------------------------------------------------------------------------
def convert_polygon(polygon):
    """Convert a polygon's coordinates from lat/lon to UTM.

    Takes in an arcpy.Polygon that uses "GCS North America 1983" (EPSG:4269)
    lat/lon coordinates. Creates and returns a new arcpy.Polygon that has
    the same vertices re-expressed in "NAD 83 UTM zone 15N" (EPSG:26915)
    coordinates.

    This conversion is actually from "WGS 1984" not "GCS 1983", but these two
    are close enough for our purposes.

    Arguments
    ---------
    polygon : arcpy.arcobjects.geometries.Polygon
        An arcpy.Polygon in lat/lon.

    Returns
    -------
    polygon : arcpy.arcobjects.geometries.Polygon
        An arcpy.Polygon in UTM 15N.
    """

    lon = [pnt.X for pnt in polygon.getPart(0)]
    lat = [pnt.Y for pnt in polygon.getPart(0)]

    sr_out = arcpy.SpatialReference(26915)
    projector = pyproj.Proj("epsg:26915", preserve_units=False)

    x, y = projector(lon, lat)
    array = arcpy.Array([arcpy.Point(xy[0], xy[1]) for xy in zip(x, y)])

    return arcpy.Geometry("polygon", array, sr_out)
