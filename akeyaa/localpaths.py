"""Local explicit paths to the necessary ArcGIS Pro/ArcPy gdb files.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
04 June 2020
"""

# Minnesota County Well Index (CWI). Obtained from the Minnesota Department
# of Health. The CWI is administered by the Minnesota Geological Survey.
# https://www.mngs.umn.edu/cwi.html
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
CWIGDB = r"D:\Google Drive\CWI\CWI_20200420\water_well_information.gdb"

# Boundaries of Minnesota. Obtained from the Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-state
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
STAGDB = r'D:\Google Drive\GIS\fgdb_bdry_state\bdry_state.gdb'

# City, Township, and Unorganized Territory in Minnesota. Obtained from the
# Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-mn-city-township-unorg
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
CTUGDB = r'D:\Google Drive\GIS\fgdb_bdry_mn_city_township_unorg\bdry_mn_city_township_unorg.gdb'

# County Boundaries, Minnesota. Obtained from the Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-counties-in-minnesota
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
CTYGDB = r'D:\Google Drive\GIS\fgdb_bdry_counties_in_minnesota\bdry_counties_in_minnesota.gdb'

# National Hydrology Products: Watershed Boundary Dataset (WBD). Obtained
# from the US Geological Survey. Beware! This gdb uses lat/lon coordinates.
# https://www.usgs.gov/core-science-systems/ngp/national-hydrography
# This gdb uses 'GCS North America 1983' (EPSG:4269).
WBDGDB = r'D:\Google Drive\GIS\WBD_National_GDB\WBD_National_GDB.gdb'

 # The location details of specific feature classes.
SOURCE = {
    "CITY":      CTUGDB + r"\city_township_unorg",      # City boundaries
    "TOWNSHIP":  CTUGDB + r"\city_township_unorg",      # Township boundaries
    "COUNTY":    CTYGDB + r"\mn_county_boundaries",     # County boundaries
    "WATERSHED": WBDGDB + r"\WBDHU10",                  # Watershed boundaries
    "SUBREGION": WBDGDB + r"\WBDHU8",                   # Subregion boundaries
    "STATE":     STAGDB + r"\Boundaries_of_Minnesota",  # MN state boundary
    "ALLWELLS":  CWIGDB + r"\allwells",                 # MN county well index
    "C5WL":      CWIGDB + r"\C5WL"                      # MN static water levels
    }
