from random import random
import time

import arcpy
import numpy as np
from scipy import spatial


CWILOC = r"D:\Google Drive\CWI\CWI_20200420\water_well_information.gdb"
WELLS = CWILOC + r'\allwells'
SWLS = CWILOC + r'\C5WL'

# Create the list of target locations.
M = 10
XMIN = 250000
XMAX = 480000
YMIN = 4800000
YMAX = 5200000

RADIUS = 10000

target = []
for m in range(M):
    xloc = XMIN + (XMAX-XMIN)*random()
    yloc = YMIN + (YMAX-YMIN)*random()
    target.append([xloc, yloc])

cnt = np.zeros((M,3))

# Create the arcpy table od selected wells.
start_time = time.perf_counter()

joined_table = arcpy.AddJoin_management(WELLS, 'RELATEID', SWLS, 'RELATEID', False)

where = ("allwells.AQUIFER = 'QBAA' AND "
         "allwells.UTME is not NULL AND "
         "allwells.UTMN is not NULL AND "
         "C5WL.MEAS_ELEV is not NULL")
selected_wells = arcpy.SelectLayerByAttribute_management(joined_table, 'NEW_SELECTION', where)

stop_time = time.perf_counter()
print('SelectLayerByAttribute: ELAPSED TIME = {0}'.format(stop_time-start_time))

# Create the python list of selected wells
start_time = time.perf_counter()

well_data = []

ATTRIBUTES = ['allwells.SHAPE', 'C5WL.MEAS_ELEV', 'allwells.RELATEID']
with arcpy.da.SearchCursor(selected_wells, ATTRIBUTES) as cursor:
    for row in cursor:
        x = row[0][0]
        y = row[0][1]
        z = row[1]
        if (x is not None) and (y is not None) and (z is not None):
            well_data.append([x, y])
        else:
            print(row)
N = len(well_data)

stop_time = time.perf_counter()
print('Extract well_data: ELAPSED TIME = {0}'.format(stop_time-start_time))

# Create the scipy.spatial.KDTree.
start_time = time.perf_counter()

tree = spatial.cKDTree(np.array(well_data))

stop_time = time.perf_counter()
print('Create the cKDTree: ELAPSED TIME = {0}'.format(stop_time-start_time))

# -------------------------------------
# arcpy.SelectByLocation
# -------------------------------------
start_time = time.perf_counter()
try:
    for m in range(M):
        point = arcpy.Point(target[m][0], target[m][1])
        active_wells = arcpy.SelectLayerByLocation_management(selected_wells,
            'WITHIN_A_DISTANCE', arcpy.PointGeometry(point), RADIUS, 'NEW_SELECTION')
        cnt[m][0] = active_wells[2]
except:
    pass

stop_time = time.perf_counter()
print('SelectLayerByLocation: ELAPSED TIME = {0}'.format(stop_time-start_time))

# -------------------------------------
# numpy linear search
# -------------------------------------
start_time = time.perf_counter()

for m in range(M):
    xtarget = target[m][0]
    ytarget = target[m][1]

    active_wells = []
    for n in range(N):
        if np.hypot(well_data[n][0]-xtarget, well_data[n][1]-ytarget) < RADIUS:
            active_wells.append(n)
    cnt[m][1] = len(active_wells)

stop_time = time.perf_counter()
print('Numpy linear search: ELAPSED TIME = {0}'.format(stop_time-start_time))

# -------------------------------------
# numpy KDTree search
# -------------------------------------
start_time = time.perf_counter()

for m in range(M):
    active_wells = tree.query_ball_point(target[m], RADIUS)
    cnt[m][2] = len(active_wells)

stop_time = time.perf_counter()
print('Numpy cKDTree search: ELAPSED TIME = {0}'.format(stop_time-start_time))

