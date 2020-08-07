"""Implement the Model class in the MVC pattern for AkeyaaPy."""

import bz2
import datetime
import pickle

__author__ = "Randal J Barnes"
__version__ = "05 August 2020"


class Model:
    def __init__(self):
        # Initialize the parameters
        self.parameters = {
            "radius" : 3000,
            "required" : 25,
            "spacing" : 1000,
            "firstyear" : 1871,
            "lastyear" : datetime.datetime.now().year
        }

        # Get the pre-digested venue data.
        pklzfile = r"..\data\Akeyaa_Venues.pklz"
        with bz2.open(pklzfile, "rb") as fileobject:
            self.venue_data = pickle.load(fileobject)

        # Get the pre-digested well data.
        pklzfile = r"..\data\Akeyaa_Wells.pklz"
        with bz2.open(pklzfile, "rb") as fileobject:
            self.well_list = pickle.load(fileobject)

    def get_parameters(self):
        return self.parameters

    def get_venue_data(self):
        return self.venue_data
