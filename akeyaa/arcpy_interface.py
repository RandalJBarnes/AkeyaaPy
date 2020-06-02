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

arcpy.da.SearchCursor(source, attributes, where)

table = arcpy.AddJoin_management(ALLWELLS, "RELATEID", C5WL, "RELATEID", False)


arcpy.SelectLayerByLocation_management(
            table,
            select_features=polygon,
            overlap_type="WITHIN",
            selection_type="NEW_SELECTION")

<venues.py>
from arcpy.da import SearchCursor
from arcpy import SpatialReference, Array, Point, Geometry

<wells.py>
arcpy.AddJoin_management
arcpy.da.SearchCursor
arcpy.SelectLayerByLocation_management

<analyze.py>
polygon.contains(arcpy.Point(xo, yo)):

"""