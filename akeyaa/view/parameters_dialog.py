"""Parameters GUI"""

__author__ = "Randal J Barnes"
__version__ = "07 August 2020"

import tkinter as tk
import tkinter.ttk as ttk

class ParametersDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.parent.wm_attributes("-disabled", True)         # Make the dialog modal

        self.title("Parameters")

        self.top_frame = tk.Frame(self)
        self.btn_frame = tk.Frame(self)

        self.top_frame.grid(row=0, column=0, padx=5, pady=5)
        self.btn_frame.grid(row=1, column=0, padx=5, pady=5, sticky="E")

        self.radius = tk.DoubleVar(value=self.parent.parameters["radius"])
        self.radius_text = tk.Label(self.top_frame, text="radius")
        self.radius_sb = tk.Spinbox(self.top_frame, textvariable=self.radius, from_=0, increment=100, to=1000000)
        self.radius_text.grid(row=0, column=0, sticky="W", padx=5)
        self.radius_sb.grid(row=0, column=1, sticky="W", padx=5)

        self.required = tk.IntVar(value=self.parent.parameters["required"])
        self.required_text = tk.Label(self.top_frame, text="required")
        self.required_sb = tk.Spinbox(self.top_frame, textvariable=self.required, from_=0, increment=1, to=10000)
        self.required_text.grid(row=1, column=0, sticky="W", padx=5)
        self.required_sb.grid(row=1, column=1, sticky="W", padx=5)

        self.spacing = tk.DoubleVar(value=self.parent.parameters["spacing"])
        self.spacing_text = tk.Label(self.top_frame, text="spacing")
        self.spacing_sb = tk.Spinbox(self.top_frame, textvariable=self.spacing, from_=0, increment=100, to=100000)
        self.spacing_text.grid(row=2, column=0, sticky="W", padx=5)
        self.spacing_sb.grid(row=2, column=1, sticky="W", padx=5)

        self.firstyear = tk.IntVar(value=self.parent.parameters["firstyear"])
        self.firstyear_text = tk.Label(self.top_frame, text="first year")
        self.firstyear_sb = tk.Spinbox(self.top_frame, textvariable=self.firstyear)
        self.firstyear_text.grid(row=3, column=0, sticky="W", padx=5)
        self.firstyear_sb.grid(row=3, column=1, sticky="W", padx=5)

        self.lastyear = tk.IntVar(value=self.parent.parameters["lastyear"])
        self.lastyear_text = tk.Label(self.top_frame, text="last year")
        self.lastyear_sb = tk.Spinbox(self.top_frame, textvariable=self.lastyear)
        self.lastyear_text.grid(row=4, column=0, sticky="W", padx=5)
        self.lastyear_sb.grid(row=4, column=1, sticky="W", padx=5)

        self.btn_okay = ttk.Button(self.btn_frame, text="OK", command=self.okay)
        self.btn_okay.grid(row=0, column=0, sticky="E")

        self.btn_cancel = ttk.Button(self.btn_frame, text="Cancel", command=self.cancel)
        self.btn_cancel.grid(row=0, column=1, sticky="E")

    def okay(self):
        self.parent.parameters = {
            "radius" : self.radius.get(),
            "required" : self.required.get(),
            "spacing" : self.spacing.get(),
            "firstyear" : self.firstyear.get(),
            "lastyear" : self.lastyear.get()
        }
        self.parent.wm_attributes("-disabled", False)
        self.destroy()

    def cancel(self):
        self.parent.wm_attributes("-disabled", False)
        self.destroy()
