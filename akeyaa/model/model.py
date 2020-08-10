"""Implement the Model class in the MVC pattern for AkeyaaPy.

This modules contains the working functions that perform the Akeyaa analysis
across a venue.

Notes
-----
*Akeyaa analysis* entails the fitting of the  conic potential model at
many target locations within the `venue`. The target locations are selected
as the nodes of a square grid covering the `venue`. The square grid of
target locations is anchored at the centroid of the `venue`'s domain,
and the grid lines are separated by `spacing`.

If a target location is not inside of the `venue` it is discarded. For each
remaining target location, all wells that satisfy the following criteria
are identified:

- the well is within a horizontal distance of `radius` of the target location,
- the well is completed in one or more of the `aquifers`,
- the water level measurement date is on or after `after`, and
- the water level measurement date is on or before `before`.

If a target location has fewer than `required` identified (neighboring)
wells it is discarded. The Akeyaa analysis is carried out at each of the
remaining target locations using the `method` for fitting the conic
potential model.

Data from outside of the venue may be used in the computations.

"""
from itertools import compress
from akeyaa.model.wells import Wells
from akeyaa.model.fit_conic_potential import fit_conic_potential

__author__ = "Randal J Barnes"
__version__ = "09 August 2020"


class Model:
    def __init__(self, well_list):
        self.wells = Wells(well_list)

    def by_venue(self, venue, settings):
        """Compute the Akeyaa analysis across the specified venue.

        Parameters
        ----------
        venue: type
            An instance of a political division, administrative region, or
            user-defined domain, as enumerated and detailed in `akeyaa.venues`.
            For example: a ``City``, ``Watershed``, or ``Neighborhood``.

        settings : type
            A complete, validated set of akeyaa parameters, as enumerated and
            detailed in `akeyaa.parameters`.

        Returns
        -------
        results : list[tuple] (xytarget, n, evp, varp)

            xytarget : tuple (float, float)
                x- and y-coordinates of target location.
            n : int
                number of naerby wells used in the local analysis.
            evp : (6, 1) ndarray
                expected value vector of the model parameters.
            varp : (6, 6) ndarray
                variance/covariance matrix of the model parameters.

        See Also
        --------
        akeyaa.parameters, akeyaa.venues, akeyaa.wells

        """
        targets = self.layout_the_targets(venue, settings.spacing)

        results = []
        for xytarget in targets:
            welldata = self.wells.fetch(
                xytarget,
                settings.radius,
                settings.aquifers,
                settings.after,
                settings.before
            )
            if len(welldata) >= settings.required:
                xyz = [row[0:2] for row in welldata]
                evp, varp = fit_conic_potential(xytarget, xyz, settings.method)
                results.append((xytarget, len(xyz), evp, varp))

        return results


    def layout_the_targets(self, venue, spacing):
        """Determine the evenly-spaced locations of the x and y grid lines.

        The grid lines of target locations are anchored at the centroid of the
        `venue`, axes-aligned, and the separated by `spacing`. The outer extent
        of the grid captures all of the vertices of the `venue`.

        The grid nodes are then filtered so that only nodes inside of the venue
        are retained.

        Parameters
        ----------
        venue: type
            An instance of a political division, administrative region, or
            user-defined domain, as enumerated and detailed in `akeyaa.venues`.
            For example: a ``City``, ``Watershed``, or ``Neighborhood``.

        spacing : float
            Grid spacing for target locations across the venue. The grid is
            square, so only one `spacing` is needed.

        Returns
        -------
        targets : list[tuple] (xtarget, ytarget)
            x- and y-coordinates of the target points.

        See Also
        --------
        akeyaa.venues

        """
        xgrd = [venue.centroid()[0]]
        while xgrd[-1] > venue.extent()[0]:
            xgrd.append(xgrd[-1] - spacing)
        xgrd.reverse()
        while xgrd[-1] < venue.extent()[1]:
            xgrd.append(xgrd[-1] + spacing)

        ygrd = [venue.centroid()[1]]
        while ygrd[-1] > venue.extent()[2]:
            ygrd.append(ygrd[-1] - spacing)
        ygrd.reverse()
        while ygrd[-1] < venue.extent()[3]:
            ygrd.append(ygrd[-1] + spacing)

        xygrd = []
        for x in xgrd:
            for y in ygrd:
                xygrd.append((x,y))
        flag = venue.contains_points(xygrd)
        return list(compress(xygrd, flag))

