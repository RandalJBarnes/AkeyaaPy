"""Neighborhood Venue Dialog"""

__author__ = "Randal J Barnes"
__version__ = "09 August 2020"

import tkinter as tk
import tkinter.ttk as ttk

class FrameDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.parent.wm_attributes("-disabled", True)        # Make the dialog modal

        self.venue = {
            "type": "Frame",
            "minimum_easting" : None,
            "maximum_easting" : None,
            "minimum_northing" : None,
            "maximum_northing" : None
        }
        self.title("Frame")

        self.top_frame = tk.Frame(self)
        self.btn_frame = tk.Frame(self)

        self.top_frame.grid(row=0, column=0, padx=5, pady=5)
        self.btn_frame.grid(row=1, column=0, padx=5, pady=5, sticky="E")

        if self.parent.venue["type"] == "Frame":
            initial_minimum_easting = self.parent.frame["minimum_easting"]
            initial_maximum_easting = self.parent.frame["maximum_easting"]
            initial_minimum_northing = self.parent.frame["minimum_northing"]
            initial_maximum_northing = self.parent.frame["maximum_northing"]
        else:
            initial_minimum_easting = 481738.99 - 10000     # Civil Engineering Building
            initial_maximum_easting = 481738.99 + 10000     # Univeristy of Minnesota
            initial_minimum_northing = 4980337.72 - 10000   # Go Gophers!
            initial_maximum_northing = 4980337.72 + 10000

        self.minimum_easting = tk.DoubleVar(value=initial_minimum_easting)
        self.maximum_easting = tk.DoubleVar(value=initial_maximum_easting)
        self.minimum_northing = tk.DoubleVar(value=initial_minimum_northing)
        self.maximum_northing = tk.DoubleVar(value=initial_maximum_northing)

        self.easting_text = tk.Label(self.top_frame, text="easting")
        self.northing_text = tk.Label(self.top_frame, text="northing")
        self.minimum_text = tk.Label(self.top_frame, text="minimum")
        self.maximum_text = tk.Label(self.top_frame, text="maximum")

        self.minimum_easting_sb = tk.Spinbox(self.top_frame, textvariable=self.minimum_easting,
                                             from_=189783, increment=100, to=761654)        # min & max for MN
        self.maximum_easting_sb = tk.Spinbox(self.top_frame, textvariable=self.maximum_easting,
                                             from_=189783, increment=100, to=761654)        # min & max for MN
        self.minimum_northing_sb = tk.Spinbox(self.top_frame, textvariable=self.minimum_northing,
                                             from_=4816309, increment=100, to=5472347)      # min & max for MN
        self.maximum_northing_sb = tk.Spinbox(self.top_frame, textvariable=self.maximum_northing,
                                             from_=4816309, increment=100, to=5472347)      # min & max for MN

        self.minimum_text.grid(row=0, column=1, sticky="W", padx=5)
        self.maximum_text.grid(row=0, column=2, sticky="W", padx=5)

        self.easting_text.grid(row=1, column=0, sticky="W", padx=5)
        self.minimum_easting_sb.grid(row=1, column=1, sticky="W", padx=5)
        self.maximum_easting_sb.grid(row=1, column=2, sticky="W", padx=5)

        self.northing_text.grid(row=2, column=0, sticky="W", padx=5)
        self.minimum_northing_sb.grid(row=2, column=1, sticky="W", padx=5)
        self.maximum_northing_sb.grid(row=2, column=2, sticky="W", padx=5)

        # Setup the button frame.
        self.btn_okay = ttk.Button(self.btn_frame, text="OK", command=self.okay)
        self.btn_okay.grid(row=0, column=0, sticky="E")

        self.btn_cancel = ttk.Button(self.btn_frame, text="Cancel", command=self.cancel)
        self.btn_cancel.grid(row=0, column=1, sticky="E")

    def okay(self):
        self.venue["minimum_easting"] = self.minimum_easting.get()
        self.venue["maximum_easting"] = self.maximum_easting.get()
        self.venue["minimum_northing"] = self.minimum_northing.get()
        self.venue["maximum_northing"] = self.maximum_northing.get()

        self.parent.venue = self.venue
        self.parent.wm_attributes("-disabled", False)
        self.destroy()

    def cancel(self):
        self.parent.wm_attributes("-disabled", False)
        self.destroy()
