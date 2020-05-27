"""
Local explicit paths to the necessary gdb files.

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
27 May 2020

"""

# Minnesota County Well Index (CWI). Obtained from the Minnesota Department
# of Health. The CWI is administered by the Minnesota Geological Survey.
# https://www.mngs.umn.edu/cwi.html
CWILOC = r"D:\Google Drive\CWI\CWI_20200420\water_well_information.gdb"

# Boundaries of Minnesota. Obtained from the Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-state
STALOC = r'D:\Google Drive\GIS\fgdb_bdry_state\bdry_state.gdb'

# County Boundaries, Minnesota. Obtained from the Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/bdry-counties-in-minnesota
CTYLOC = r'D:\Google Drive\GIS\fgdb_bdry_counties_in_minnesota\bdry_counties_in_minnesota.gdb'

# Township, Range, and Section (TRS) Boundaries Minnesota. Obtained from the
# Minnesota Geospatial Commons.
# https://gisdata.mn.gov/dataset/plan-mngeo-trs
TRSLOC = r'D:\Google Drive\GIS\fgdb_plan_mngeo_trs\plan_mngeo_trs.gdb'

# National Hydrology Products: Watershed Boundary Dataset (WBD). Obtained
# from the US Geological Survey
# https://www.usgs.gov/core-science-systems/ngp/national-hydrography
# Beware! This gdb uses lat/lon coordinates; more specifically 'GRS 1980'
# (EPSG:7019), which is a precursor of 'WGS 84' (EPSG:4326).
WBDLOC = r'D:\Google Drive\GIS\WBD_National_GDB\WBD_National_GDB.gdb'
