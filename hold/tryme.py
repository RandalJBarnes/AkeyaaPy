import time

import arcpy
import numpy as np
from scipy import spatial


CWILOC = r"D:\Google Drive\CWI\CWI_20200420\water_well_information.gdb"
WELLS = CWILOC + r'\allwells'
SWLS = CWILOC + r'\C5WL'

# -----------------
start_time = time.perf_counter()

joined_table = arcpy.AddJoin_management(WELLS, 'RELATEID', SWLS, 'RELATEID', False)

where = ("AQUIFER = 'QBAA' AND "
         "UTME is not NULL AND "
         "UTMN is not NULL AND "
         "SWL = 'Y' AND "
         "MEAS_ELEV is not NULL")

ATTRIBUTES = ['allwells.SHAPE', 'C5WL.MEAS_ELEV']

well_list = []
with arcpy.da.SearchCursor(joined_table, ATTRIBUTES, where) as cursor:
    for row in cursor:
        well_list.append([row[0][0], row[0][1], row[1]])
well_data = np.array(well_list)

stop_time = time.perf_counter()
print('ELAPSED TIME = {0}'.format(stop_time-start_time))

# -----------------
# Create the scipy.spatial.KDTree.
start_time = time.perf_counter()

tree = spatial.cKDTree(np.array(well_data[:, 0:2]))

stop_time = time.perf_counter()
print('Create the cKDTree: ELAPSED TIME = {0}'.format(stop_time-start_time))
