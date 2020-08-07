"""Create zipped pickle files containing the venue data for Minnesota.

This program extracts the necessary venue data from the ArcGIS Pro global data
bases (.gdb) allowing AkeyaaPy to run independently.

This program (file) is meant to be run as as a stand-alone script. This program
is not meant to be distributed with AkeyaaPy. However, the resulting data files
are part of the AkeyaaPy distribution.

Requires
--------
* arcpy     this includes ESRI's arcgis and arcgispro.
* pyproj    Python interface to the proj.4 library.
* bzip2

Notes
_____
* There are five venue types included: City, Township, County, Watershed,
    and Subregion.

* The associated zipped pickle files are named:
    City      --> "Akeyaa_City.pklz",
    Township  --> "Akeyaa_Township.pklz",
    County    --> "Akeyaa_County.pklz",
    Watershed --> "Akeyaa_Watershed.pklz",
    Subregion --> "Akeyaa_Subregion.pklz",

* Each venue includes four components: a name, an identifying number or
    id string, a list of polygon vertices, and the centroid of the polygon.

* All coordinates, polygon vertices and centroids, are given in Minnesota's
    standard 'NAD 1983 UTM zone 15N' (EPSG:26915).

"""
import numpy as np
import pyproj
import arcpy
import bz2
import pickle

__author__ = "Randal J Barnes"
__version__ = "03 August 2020"


# City, Township, and Unorganized Territory in Minnesota. Obtained from the
# Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-mn-city-township-unorg
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
CTUGDB = r"D:\Google Drive\GIS\fgdb_bdry_mn_city_township_unorg\bdry_mn_city_township_unorg.gdb"

# County Boundaries, Minnesota. Obtained from the Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-counties-in-minnesota
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
CTYGDB = r"D:\Google Drive\GIS\fgdb_bdry_counties_in_minnesota\bdry_counties_in_minnesota.gdb"

# National Hydrology Products: Watershed Boundary Dataset (WBD). Obtained
# from the US Geological Survey. Beware! This gdb uses lat/lon coordinates.
# https://www.usgs.gov/core-science-systems/ngp/national-hydrography
# This gdb uses 'GCS North America 1983' (EPSG:4269).
WBDGDB = r"D:\Google Drive\GIS\WBD_National_GDB\WBD_National_GDB.gdb"

# Boundaries of Minnesota. Obtained from the Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-state
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
STAGDB = r"D:\Google Drive\GIS\fgdb_bdry_state\bdry_state.gdb"


# The location details of specific feature classes.
SOURCE = {
    "CITY"      : CTUGDB + r"\city_township_unorg",     # City boundaries
    "TOWNSHIP"  : CTUGDB + r"\city_township_unorg",     # Township boundaries
    "COUNTY"    : CTYGDB + r"\mn_county_boundaries",    # County boundaries
    "WATERSHED" : WBDGDB + r"\WBDHU10",                 # Watershed boundaries
    "SUBREGION" : WBDGDB + r"\WBDHU8",                  # Subregion boundaries
    "STATE"     : STAGDB + r"\Boundaries_of_Minnesota", # MN state boundary
}

def get_venue_data(source, what, where):
    venue_list = []
    with arcpy.da.SearchCursor(source, what, where) as cursor:
        for row in cursor:
            name = row[0]
            code = row[1]
            poly = row[2]

            x = []
            y = []
            for pnt in poly.getPart(0):
                try:
                    x.append(pnt.X)
                    y.append(pnt.Y)
                except:
                    pass

            if poly.spatialReference.type == "Geographic":
                # Convert lat/lon coordinates, GCS North America 1983 (EPSG:4269),
                # to UTM coordinate, NAD 83 UTM zone 15N (EPSG:26915).
                projector = pyproj.Proj("epsg:26915", preserve_units=False)
                x, y = projector(x, y)

            vertices = np.column_stack((x, y))
            centroid = (poly.centroid.X, poly.centroid.Y)
            venue_list.append((name, code, vertices, centroid))

    return venue_list

if __name__ == "__main__":
    # execute only if run as a script

    # Get City data
    source = SOURCE["CITY"]
    what = ["NAME", "GNIS_ID", "SHAPE@"]
    where = "(CTU_Type = 'CITY')"
    city_list = get_venue_data(source, what, where)

    # Get Township data
    source = SOURCE["TOWNSHIP"]
    what = ["NAME", "GNIS_ID", "SHAPE@"]
    where = "(CTU_Type = 'TOWNSHIP')"
    township_list = get_venue_data(source, what, where)

    # Get County data
    source = SOURCE["COUNTY"]
    what = ["CTY_NAME", "CTY_FIPS", "SHAPE@"]
    where = ""
    county_list = get_venue_data(source, what, where)

    # Get Watershed data
    source = SOURCE["WATERSHED"]
    what = ["NAME", "HUC10", "SHAPE@"]
    where = "(STATES LIKE '%MN%')"
    watershed_list = get_venue_data(source, what, where)

    # Get Subregion data
    source = SOURCE["SUBREGION"]
    what = ["NAME", "HUC8", "SHAPE@"]
    where = "(STATES LIKE '%MN%')"
    subregion_list = get_venue_data(source, what, where)

    # Get the Minnesota State boundary.
    source = SOURCE["STATE"]
    what = ["STATE_NAME", "STATE_FIPS_CODE", "SHAPE@"]
    where = "STATE_NAME = 'Minnesota'"
    minnesota_list = get_venue_data(source, what, where)

    # Create the omnibus zipped pickle file of venue data.
    archive = {
        "city_list": city_list,
        "township_list": township_list,
        "county_list": county_list,
        "watershed_list": watershed_list,
        "subregion_list": subregion_list,
        "minnesota_list": minnesota_list
    }

    pklzfile = "Akeyaa_Venues.pklz"
    with bz2.open(pklzfile, "wb") as fileobject:
        pickle.dump(archive, fileobject)
