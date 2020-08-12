"""Neighborhood Venue Dialog"""

__author__ = "Randal J Barnes"
__version__ = "10 August 2020"

import tkinter as tk
import tkinter.ttk as ttk

class NeighborhoodDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.parent.wm_attributes("-disabled", True)        # Make the dialog modal

        self.venue = {
            "type" : "Neighborhood",
            "easting" : None,
            "northing" : None,
            "radius" : None
        }
        self.title("Neighborhood")

        self.top_frame = tk.Frame(self)
        self.btn_frame = tk.Frame(self)

        self.top_frame.grid(row=0, column=0, padx=5, pady=5)
        self.btn_frame.grid(row=1, column=0, padx=5, pady=5, sticky="E")

        if self.parent.selected_venue["type"] == "Neighborhood":
            initial_easting = self.parent.selected_venue["easting"]
            initial_northing = self.parent.selected_venue["northing"]
            initial_radius = self.parent.selected_venue["radius"]
        else:
            initial_easting = 481738.99         # Civil Engineering Building
            initial_northing = 4980337.72       # Univeristy of Minnesota
            initial_radius = 10000              # Go Gophers!

        self.easting = tk.DoubleVar(value=initial_easting)
        self.easting_text = tk.Label(self.top_frame, text="easting")
        self.easting_sb = tk.Spinbox(self.top_frame, textvariable=self.easting,
                                     from_=189783, increment=100, to=761654)        # min & max for MN

        self.northing = tk.DoubleVar(value=initial_northing)
        self.northing_text = tk.Label(self.top_frame, text="northing")
        self.northing_sb = tk.Spinbox(self.top_frame, textvariable=self.northing,
                                      from_=4816309, increment=100, to=5472347)     # min & max for MN

        self.radius = tk.DoubleVar(value=initial_radius)
        self.radius_text = tk.Label(self.top_frame, text="radius")
        self.radius_sb = tk.Spinbox(self.top_frame, textvariable=self.radius, from_=0, increment=100, to=1000000)

        self.easting_text.grid(row=0, column=0, sticky="W", padx=5)
        self.northing_text.grid(row=1, column=0, sticky="W", padx=5)
        self.radius_text.grid(row=2, column=0, sticky="W", padx=5)

        self.easting_sb.grid(row=0, column=1, sticky="W", padx=5)
        self.northing_sb.grid(row=1, column=1, sticky="W", padx=5)
        self.radius_sb.grid(row=2, column=1, sticky="W", padx=5)

        # Setup the button frame.
        self.btn_okay = ttk.Button(self.btn_frame, text="OK", command=self.okay)
        self.btn_okay.grid(row=0, column=0, sticky="E")

        self.btn_cancel = ttk.Button(self.btn_frame, text="Cancel", command=self.cancel)
        self.btn_cancel.grid(row=0, column=1, sticky="E")

    def okay(self):
        self.venue["easting"] = self.easting.get()
        self.venue["northing"] = self.northing.get()
        self.venue["radius"] = self.radius.get()

        self.parent.selected_venue = self.venue
        self.parent.wm_attributes("-disabled", False)
        self.destroy()

    def cancel(self):
        self.parent.wm_attributes("-disabled", False)
        self.destroy()
