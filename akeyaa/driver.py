"""Implement the Driver class for AkeyaaPy.


   well_list : list[tuple] (xy, z, aquifer, relateid)
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
            Recorded measurement date written as YYYYMMDD.

        For example: ((232372.0, 5377518.0), 964.0, 'QBAA', '0000153720', '19650322')

"""
import bz2
import pickle
import numpy as np

from akeyaa.wells import Wells
from akeyaa.view import View
from akeyaa.venues import City, Township, County, Watershed, Subregion, Neighborhood, Frame
from akeyaa.model import model_by_venue
from akeyaa.show import show_by_venue
from akeyaa.geology import show_aquifers_by_venue

__author__ = "Randal J Barnes"
__version__ = "16 August 2020"


# The following is a complete list of all 4-character aquifer codes used in
# the Minnesota County Well index as of 1 January 2020. There are 10 groups
# by first letter: {C, D, I, K, M, O, P, Q, R, U}.
ALL_AQUIFERS = {
    "CAMB", "CECR", "CEMS", "CJDN", "CJDW", "CJMS", "CJSL", "CJTC", "CLBK",
    "CMFL", "CMRC", "CMSH", "CMTS", "CSLT", "CSLW", "CSTL", "CTCE", "CTCG",
    "CTCM", "CTCW", "CTLR", "CTMZ", "CWEC", "CWMS", "CWOC",
    "DCLP", "DCLS", "DCOG", "DCOM", "DCVA", "DCVL", "DCVU", "DEVO", "DPOG",
    "DPOM", "DSOG", "DSOM", "DSPL", "DWAP", "DWPR",
    "INDT",
    "KDNB", "KREG", "KRET",
    "MTPL",
    "ODCR", "ODGL", "ODPL", "ODUB", "OGCD", "OGCM", "OGDP", "OGPC", "OGPD",
    "OGPR", "OGSC", "OGSD", "OGSV", "OGVP", "OGWD", "OMAQ", "OMQD", "OMQG",
    "OPCJ", "OPCM", "OPCT", "OPCW", "OPDC", "OPGW", "OPNR", "OPOD", "OPSH",
    "OPSP", "OPVJ", "OPVL", "OPWR", "ORDO", "ORRV", "OSCJ", "OSCM", "OSCS",
    "OSCT", "OSPC", "OSTP", "OWIN",
    "PAAI", "PAAM", "PABD", "PABG", "PABK", "PACG", "PAEF", "PAES", "PAEY",
    "PAFL", "PAFR", "PAFV", "PAGR", "PAGU", "PAJL", "PAKG", "PALC", "PALG",
    "PALL", "PALP", "PALS", "PALT", "PALV", "PAMB", "PAMC", "PAMD", "PAMG",
    "PAML", "PAMR", "PAMS", "PAMT", "PAMU", "PAMV", "PANB", "PANL", "PANS",
    "PANU", "PAOG", "PAQF", "PASG", "PASH", "PASL", "PASM", "PASN", "PASR",
    "PAST", "PASZ", "PATL", "PAUD", "PAVC", "PAWB", "PCCR", "PCRG", "PCUU",
    "PEAG", "PEAL", "PEBC", "PEBI", "PEDN", "PEDQ", "PEFG", "PEFH", "PEFM",
    "PEGT", "PEGU", "PEHL", "PEIL", "PELF", "PELR", "PEMG", "PEML", "PEMN",
    "PEMU", "PEPG", "PEPK", "PEPP", "PEPZ", "PERB", "PERF", "PERV", "PESC",
    "PEST", "PESX", "PETR", "PEUD", "PEVT", "PEWR", "PEWT", "PEWV", "PMBB",
    "PMBE", "PMBI", "PMBL", "PMBM", "PMBO", "PMBR", "PMCV", "PMDA", "PMDC",
    "PMDE", "PMDF", "PMDL", "PMEP", "PMES", "PMFL", "PMGI", "PMGL", "PMHF",
    "PMHN", "PMHR", "PMLD", "PMMU", "PMNF", "PMNI", "PMNL", "PMNM", "PMNS",
    "PMPA", "PMRC", "PMSU", "PMTH", "PMUD", "PMUS", "PMVU", "PMWL", "PUDF",
    "QBAA", "QBUA", "QUUU", "QWTA",
    "RUUU",
    "UREG"
}


class Driver:
    def __init__(self):
        # Get the pre-digested well data.
        pklzfile = r"..\data\Akeyaa_Wells.pklz"
        with bz2.open(pklzfile, "rb") as fileobject:
            self.well_list = pickle.load(fileobject)
        self.wells = Wells(self.well_list)

        # Get the pre-digested venue data.
        pklzfile = r"..\data\Akeyaa_Venues.pklz"
        with bz2.open(pklzfile, "rb") as fileobject:
            self.venue_data = pickle.load(fileobject)

        # Execute the graphical user interface.
        self.view = View(self.venue_data, self.run_callback)
        self.view.mainloop()

    def run_callback(self, selected_venue, selected_aquifers, parameters):
        # Create the requested Venue.
        if selected_venue["type"] == "City":
            city_list = self.venue_data["city_list"]
            venue = City(
                name=selected_venue["name"],
                code=selected_venue["code"],
                vertices=city_list[selected_venue["index"]][2]
            )
        elif selected_venue["type"] == "Township":
            township_list = self.venue_data["township_list"]
            venue = Township(
                name=selected_venue["name"],
                code=selected_venue["code"],
                vertices=township_list[selected_venue["index"]][2]
            )
        elif selected_venue["type"] == "County":
            county_list = self.venue_data["county_list"]
            venue = County(
                name=selected_venue["name"],
                code=selected_venue["code"],
                vertices=county_list[selected_venue["index"]][2]
            )
        elif selected_venue["type"] == "Watershed":
            watershed_list = self.venue_data["watershed_list"]
            venue = Watershed(
                name=selected_venue["name"],
                code=selected_venue["code"],
                vertices=watershed_list[selected_venue["index"]][2]
            )
        elif selected_venue["type"] == "Subregion":
            subregion_list = self.venue_data["subregion_list"]
            venue = Subregion(
                name=selected_venue["name"],
                code=selected_venue["code"],
                vertices=subregion_list[selected_venue["index"]][2]
            )
        elif selected_venue["type"] == "Neighborhood":
            venue = Neighborhood(
                name=selected_venue["name"],
                point=np.array([selected_venue["easting"], selected_venue["northing"]], dtype=float),
                radius=selected_venue["radius"]
            )
        elif selected_venue["type"] == "Frame":
            venue = Frame(
                name=selected_venue["name"],
                xmin=selected_venue["minimum_easting"],
                xmax=selected_venue["maximum_easting"],
                ymin=selected_venue["minimum_northing"],
                ymax=selected_venue["maximum_northing"],
            )
        else:
            raise ValueError("Unknown venue type")

        # Create the complete list of requested aquifers.
        aquifers = []
        for aquifer in ALL_AQUIFERS:
            if aquifer[0] in selected_aquifers:
                aquifers.append(aquifer)

        print("EXECUTE AKEYAA")
        print(f"{selected_venue}")
        print(f"{selected_aquifers}")
        print(f"{parameters}")

        show_aquifers_by_venue(self.wells, venue, aquifers, parameters["firstyear"], parameters["lastyear"])

        results = model_by_venue(self.wells, venue, aquifers, parameters)
        show_by_venue(venue, results)
