"""


"""

import arcpy


#-----------------------------------------------------------------------------------------
class Point(arcpy.Point):
    pass

#-----------------------------------------------------------------------------------------
class Array(arcpy.Array):
    pass

#-----------------------------------------------------------------------------------------
class Polygon(arcpy.Polygon):
    pass

#-----------------------------------------------------------------------------------------
class SpatialReference(arcpy.SpatialReference):
    pass

"""
<venues.py>
arcpy.da.SearchCursor
arcpy.SpatialReference
arcpy.Array
arcpy.Point
arcpy.Geometry

<wells.py>
arcpy.AddJoin_management
arcpy.da.SearchCursor
arcpy.SelectLayerByLocation_management

<analyze.py>
polygon.contains(arcpy.Point(xo, yo)):

<show.py>
xbdry = [pnt.X for pnt in venue.polygon.getPart(0)]

"""