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
import datetime
import pickle

from akeyaa.model.model import Model
from akeyaa.view.view import View

__author__ = "Randal J Barnes"
__version__ = "09 August 2020"


class Controller:
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


        self.model = Model(self.well_list)


        self.view = View(self.parameters, self.venue_data, self.run_callback)
        self.view.mainloop()



    def run_callback(self, venue, parameters):
        print("EXECUTE AKEYAA")
        print(f"{venue}")
        print(f"{parameters}")

