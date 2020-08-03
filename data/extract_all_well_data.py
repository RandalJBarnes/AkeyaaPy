"""Create zipped pickle files containing the well data for Minnesota.

This program extracts the necessary well data from the ArcGIS Pro global data
bases (.gdb) allowing AkeyaaPy to run independently.

This program (file) is meant to be run as as a stand-alone script. This program
is not meant to be distributed with AkeyaaPy. However, the resulting data file
is part of the AkeyaaPy distribution.

Notes
-----
* The resulting zipped pickle file is named: "Akeyaa_Well.pklz".

* The file contains a list of welldata, where

    welldata : list[tuple] ((x, y), z, aquifer, relateid)
        (x, y) : tuple(float, float)
            The x- and y-coordinates in "NAD 83 UTM 15N" (EPSG:26915) [m].

        z : float
            The measured static water level [ft]

        aquifer : str
            The 4-character aquifer abbreviation string, as defined in
            Minnesota Geologic Survey's coding system.

        relateid : str
            The unique 10-digit well number encoded as a string with
            leading zeros.

        For example: ((232372.0, 5377518.0), 964.0, 'QBAA', '0000153720')

"""
import arcpy
import bz2
import pickle

__author__ = "Randal J Barnes"
__version__ = "03 August 2020"


# Minnesota County Well Index (CWI). Obtained from the Minnesota Department
# of Health. The CWI is administered by the Minnesota Geological Survey.
# https://www.mngs.umn.edu/cwi.html
# This gdb uses 'NAD 1983 UTM zone 15N' (EPSG:26915).
CWIGDB = r"D:\Google Drive\CWI\CWI_20200420\water_well_information.gdb"

# The location details of specific feature classes.
SOURCE = {
    "ALLWELLS"  : CWIGDB + r"\allwells",                # MN county well index
    "C5WL"      : CWIGDB + r"\C5WL",                    # MN static water levels
}


if __name__ == "__main__":
    # execute only if run as a script

    source = arcpy.AddJoin_management(
        SOURCE["ALLWELLS"], "RELATEID", SOURCE["C5WL"], "RELATEID", False
    )

    what = [
        "allwells.SHAPE",
        "C5WL.MEAS_ELEV",
        "allwells.AQUIFER",
        "allwells.RELATEID",
        "C5WL.MEAS_DATE",
    ]

    where = (
        "(C5WL.MEAS_ELEV is not NULL) AND "
        "(allwells.AQUIFER is not NULL) AND "
        "(allwells.UTME is not NULL) AND "
        "(allwells.UTMN is not NULL)"
    )

    with arcpy.da.SearchCursor(source, what, where) as cursor:
        well_list = list(cursor)

    pklzfile = "Akeyaa_Well.pklz"
    with bz2.open(pklzfile, "wb") as fileobject:
        pickle.dump(well_list, fileobject)
