"""


"""

import arcpy


#-----------------------------------------------------------------------------------------
class Point(arcpy.arcobjects.arcobjects.Point):
    pass

#-----------------------------------------------------------------------------------------
class Array(arcpy.arcobjects.arcobjects.Point):
    pass

#-----------------------------------------------------------------------------------------
class Polygon(arcpy.arcobjects.arcobjects.Polygon):
    pass

#-----------------------------------------------------------------------------------------
class SpatialReference(arcpy.arcobjects.arcobjects.SpatialReference):
    pass



arcpy.da.SearchCursor(source, attributes, where)

table = arcpy.AddJoin_management(ALLWELLS, "RELATEID", C5WL, "RELATEID", False)


arcpy.SelectLayerByLocation_management(
            table,
            select_features=polygon,
            overlap_type="WITHIN",
            selection_type="NEW_SELECTION")