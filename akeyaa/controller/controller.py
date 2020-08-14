"""Implement the Controller class in the MVC pattern for AkeyaaPy.


   welldata : list[tuple] (xy, z, aquifer, relateid)
        xy : tuple (float, float)
            The x- and y-coordinates in "NAD 83 UTM 15N" (EPSG:26915) [m].

        z : float
            The recorded static water level [ft]

        aquifer : str
            The 4-character aquifer abbreviation string, as defined in
            Minnesota Geologic Survey's coding system.

        relateid : str
            The unique 10-digit well number encoded as a string with
            leading zeros.

        date : int
            Recorded measurement date writeen as YYYYMMDD.

        For example: ((232372.0, 5377518.0), 964.0, 'QBAA', '0000153720', '19650322')

"""
import bz2

import pickle
import numpy as np

from akeyaa.model.model import Model
from akeyaa.input.view import View
from akeyaa.controller.venues import City, Township, County, Watershed, Subregion, Neighborhood, Frame


__author__ = "Randal J Barnes"
__version__ = "11 August 2020"


class Controller:
    def __init__(self):

        # Initialize the parameters

        # Get the pre-digested venue data.
        pklzfile = r"..\data\Akeyaa_Venues.pklz"
        with bz2.open(pklzfile, "rb") as fileobject:
            self.venue_data = pickle.load(fileobject)

        # Get the pre-digested well data.
        pklzfile = r"..\data\Akeyaa_Wells.pklz"
        with bz2.open(pklzfile, "rb") as fileobject:
            self.well_list = pickle.load(fileobject)

        self.model = Model(self.well_list)

        self.view = View(self.venue_data, self.run_callback)
        self.view.mainloop()

    def run_callback(self, selected_venue, selected_aquifers, selected_parameters):

        if selected_venue["type"] == "City":
            city_list = self.venue_data["city_list"]
            venue = City(
                selected_venue["name"],
                selected_venue["code"],
                city_list[selected_venue["index"]][2]
            )

        elif selected_venue["type"] == "Township":
            township_list = self.venue_data["township_list"]
            venue = Township(
                selected_venue["name"],
                selected_venue["code"],
                township_list[selected_venue["index"]][2]
            )

        elif selected_venue["type"] == "County":
            county_list = self.venue_data["county_list"]
            venue = County(
                selected_venue["name"],
                selected_venue["code"],
                county_list[selected_venue["index"]][2]
            )

        elif selected_venue["type"] == "Watershed":
            watershed_list = self.venue_data["watershed_list"]
            venue = Watershed(
                selected_venue["name"],
                selected_venue["code"],
                watershed_list[selected_venue["index"]][2]
            )

        elif selected_venue["type"] == "Subregion":
            subregion_list = self.venue_data["subregion_list"]
            venue = Subregion(
                selected_venue["name"],
                selected_venue["code"],
                subregion_list[selected_venue["index"]][2]
            )

        elif selected_venue["type"] == "Neighborhood":
            venue = Neighborhood(
                selected_venue["name"],
                np.array([selected_venue["easting"], selected_venue["northing"]], dtype=float),
                selected_venue["radius"]
            )

        elif selected_venue["type"] == "Frame":
            venue = Frame(
                xmin = selected_venue["minimum_easting"],
                xmax = selected_venue["maximum_easting"],
                ymin = selected_venue["minimum_northing"],
                ymax = selected_venue["maximum_northing"],
            )

        else:
            raise ValueError("Unknown venue type")

        print("EXECUTE AKEYAA")
        print(f"{selected_venue}")
        print(f"{parameters}")
        print(f"{venue.fullname()}")

        self.view.plot_venue(venue)
