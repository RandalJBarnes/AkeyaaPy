========
AkeyaaPy
========

Compute flow directions using a locally-fitted conic discharge potential model.


Venues
------
A **venue** is an instance of a political division, administrative region, or user-defined domain, as enumerated and detailed in `venues.py`. The defined venues
currently include:

    - City
    - Township
    - County
    - Watershed
    - Subregion
    - Neighborhood
    - Frame
    - Patch


Data
----
The static water level data used in the analysis comes from the Minnesota County Well Index (CWI).

    - County Well Index

        - ``water_well_information.gdb``
        - The Minnesota Geological Survey
        - <https://www.mngs.umn.edu/cwi.html>

Geographic information is extracted from four other databases.

    - City, Township, and Unorganized Territory in Minnesota

        - ``bdry_mn_city_township_unorg.gdb``
        - The Minnesota Geospatial Commons
        - <https://gisdata.mn.gov/dataset/bdry-mn-city-township-unorg>

    - County Boundaries, Minnesota

        - ``bdry_counties_in_minnesota.gdb``
        - The Minnesota Geospatial Commons
        - <https://gisdata.mn.gov/dataset/bdry-counties-in-minnesota>

    - Boundaries of Minnesota

        - ``bdry_state.gdb``
        - The Minnesota Geospatial Commons
        - <https://gisdata.mn.gov/dataset/bdry-state>

    - National Hydrology Products: Watershed Boundary Dataset (WBD)

        - ``WBD_National_GDB.gdb``
        - US Geological Survey
        - <https://www.usgs.gov/core-science-systems/ngp/national-hydrography>

Method
------
The Akeyaa analysis is carried out at target locations within a selected **venue**. The target locations are selected as the nodes of a square grid
covering the **venue**.

The square grid of target locations is anchored at the centroid of the **venue**, and the grid lines are separated by `spacing`. If a target
location is not inside of the **venue** it is discarded.

For each remaining target location, all wells that satisfy the following criteria are identified:

- the well is within a horizontal distance of `radius` of the target location,
- the well is completed in one or more of the `aquifers`,
- the water level measurement date is on or after `after`, and
- the water level measurement date is on or before `before`.

If a target location has fewer than `required` identified (neighboring) wells it is discarded.

The Akeyaa analysis is carried out at each of the remaining target locations using the `method` for fitting the conic potential model.

Data from outside of the venue may also be used in the computations. However, only data from the Minnesota CWI are considered.


