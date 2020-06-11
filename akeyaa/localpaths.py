"""Local explicit paths to the necessary ArcGIS Pro/ArcPy gdb files."""

# Minnesota County Well Index (CWI). Obtained from the Minnesota Department
# of Health. The CWI is administered by the Minnesota Geological Survey.
# https://www.mngs.umn.edu/cwi.html
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
CWIGDB = r"D:\Google Drive\CWI\CWI_20200420\water_well_information.gdb"

# Boundaries of Minnesota. Obtained from the Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-state
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
STAGDB = r"D:\Google Drive\GIS\fgdb_bdry_state\bdry_state.gdb"

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
