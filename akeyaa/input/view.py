"""Implement the View class in the adapted MVC design pattern for AkeyaaPy."""

import datetime
import tkinter as tk
import tkinter.ttk as ttk

from akeyaa.input.venue_widget import VenueWidget

__author__ = "Randal J Barnes"
__version__ = "13 August 2020"


class View(tk.Tk):
    def __init__(self, venue_data, run_callback):
        super().__init__()

        # Initialize.
        self.venue_data = venue_data
        self.selected_venue = {
            "type": None,
            "aquifers": None
        }
        self.run_callback = run_callback

        # Main window.
        self.title("AkeyaaPy")

        # Set up the four main frames
        venue_frame = ttk.LabelFrame(self, text="Venue", padding=5)
        parameters_frame = ttk.LabelFrame(self, text="Parameters", padding=5)
        aquifers_frame = ttk.LabelFrame(self, text="Aquifers", padding=5)
        buttons_frame = ttk.Frame(self, padding=5)

        venue_frame.grid(row=0, column=0, rowspan=2, sticky=tk.NW)
        aquifers_frame.grid(row=0, column=1, rowspan=2, sticky=tk.NW)
        parameters_frame.grid(row=0, column=2, sticky=tk.NW)
        buttons_frame.grid(row=1, column=2, columnspan=2, sticky=tk.E)

        # Fill the Venue frame
        venue_types = ["City", "Township", "County", "Watershed", "Subregion", "Neighborhood", "Frame"]
        self.venue_type = tk.StringVar(value=self.selected_venue["type"])

        venue_text = ttk.Label(venue_frame, text="type")
        venue_cb = ttk.Combobox(
            venue_frame,
            state="readonly",
            textvariable=self.venue_type,
            values=venue_types
        )
        venue_cb.bind('<<ComboboxSelected>>', self.on_venue_type_select)

        venue_text.grid(row=0, column=0, sticky=tk.W)
        venue_cb.grid(row=0, column=1, sticky=tk.W)

        # Fill the City frame (a sub-frame in the Venue frame).
        self.venue_city_frame = ttk.Frame(venue_frame)
        venue_city_widget = VenueWidget(self.venue_city_frame, venue_data["city_list"])
        venue_city_widget.pack()

        # Fill the Township frame (a sub-frame in the Venue frame).
        self.venue_township_frame = ttk.Frame(venue_frame)
        venue_township_widget = VenueWidget(self.venue_township_frame, venue_data["township_list"])
        venue_township_widget.pack()

        # Fill the County frame (a sub-frame in the Venue frame).
        self.venue_county_frame = ttk.Frame(venue_frame)
        venue_county_widget = VenueWidget(self.venue_county_frame, venue_data["county_list"])
        venue_county_widget.pack()

        # Fill the Watershed frame (a sub-frame in the Venue frame).
        self.venue_watershed_frame = ttk.Frame(venue_frame)
        venue_watershed_widget = VenueWidget(self.venue_watershed_frame, venue_data["watershed_list"])
        venue_watershed_widget.pack()

        # Fill the Subregion frame (a sub-frame in the Venue frame).
        self.venue_subregion_frame = ttk.Frame(venue_frame)
        venue_subregion_widget = VenueWidget(self.venue_subregion_frame, venue_data["subregion_list"])
        venue_subregion_widget.pack()

        # Fill the Neighborhood frame (a sub-frame in the Venue frame).
        self.venue_neighborhood_frame = ttk.Frame(venue_frame)

        self.neighborhood_easting = tk.DoubleVar(value=481738.99)               # Civil Engineering Building
        self.neighborhood_northing = tk.DoubleVar(value=4980337.72)             # Univeristy of Minnesota
        self.neighborhood_radius = tk.DoubleVar(value=10000)                    # Go Gophers!

        easting_text = ttk.Label(self.venue_neighborhood_frame, text="easting")
        easting_sb = ttk.Spinbox(
            self.venue_neighborhood_frame,
            textvariable=self.neighborhood_easting,
            from_=189783, increment=100, to=761654                              # min & max for MN
        )

        northing_text = ttk.Label(self.venue_neighborhood_frame, text="northing")
        northing_sb = ttk.Spinbox(
            self.venue_neighborhood_frame,
            textvariable=self.neighborhood_northing,
            from_=4816309, increment=100, to=5472347                            # min & max for MN
        )

        radius_text = ttk.Label(self.venue_neighborhood_frame, text="radius")
        radius_sb = ttk.Spinbox(
            self.venue_neighborhood_frame,
            textvariable=self.neighborhood_radius,
            from_=0, increment=100, to=1000000
        )

        easting_text.grid(row=0, column=0, sticky=tk.W, pady=2)
        easting_sb.grid(row=0, column=1, sticky=tk.W, pady=2)
        northing_text.grid(row=1, column=0, sticky=tk.W, pady=2)
        northing_sb.grid(row=1, column=1, sticky=tk.W, pady=2)
        radius_text.grid(row=2, column=0, sticky=tk.W, pady=2)
        radius_sb.grid(row=2, column=1, sticky=tk.W, pady=2)

        # Fill the Frame frame (a sub-frame in the Venue frame).
        self.venue_frame_frame = ttk.Frame(venue_frame)

        self.minimum_easting = tk.DoubleVar(value=481738.99 - 10000)            # Civil Engineering Building
        self.maximum_easting = tk.DoubleVar(value=481738.99 + 10000)            # Univeristy of Minnesota
        self.minimum_northing = tk.DoubleVar(value=4980337.72 - 10000)          # Go Gophers!
        self.maximum_northing = tk.DoubleVar(value=4980337.72 + 10000)

        easting_text = tk.Label(self.venue_frame_frame, text="easting")
        northing_text = tk.Label(self.venue_frame_frame, text="northing")
        minimum_text = tk.Label(self.venue_frame_frame, text="minimum")
        maximum_text = tk.Label(self.venue_frame_frame, text="maximum")

        minimum_easting_sb = tk.Spinbox(
            self.venue_frame_frame,
            textvariable=self.minimum_easting,
            from_=189783, increment=100, to=761654                              # min & max for MN
        )

        maximum_easting_sb = tk.Spinbox(
            self.venue_frame_frame,
            textvariable=self.maximum_easting,
            from_=189783, increment=100, to=761654                              # min & max for MN
        )

        minimum_northing_sb = tk.Spinbox(
            self.venue_frame_frame,
            textvariable=self.minimum_northing,
            from_=4816309, increment=100, to=5472347                            # min & max for MN
        )

        maximum_northing_sb = tk.Spinbox(
            self.venue_frame_frame,
            textvariable=self.maximum_northing,
            from_=4816309, increment=100, to=5472347                            # min & max for MN
        )

        minimum_text.grid(row=0, column=1, sticky=tk.W)
        maximum_text.grid(row=0, column=2, sticky=tk.W)

        easting_text.grid(row=1, column=0, sticky=tk.W, pady=2)
        minimum_easting_sb.grid(row=1, column=1, sticky=tk.W, pady=2)
        maximum_easting_sb.grid(row=1, column=2, sticky=tk.W, pady=2)

        northing_text.grid(row=2, column=0, sticky=tk.W, pady=2)
        minimum_northing_sb.grid(row=2, column=1, sticky=tk.W, pady=2)
        maximum_northing_sb.grid(row=2, column=2, sticky=tk.W, pady=2)

        # Fill the Aquifers frame.
        self.cxxx = tk.BooleanVar(value=True)
        self.dxxx = tk.BooleanVar(value=True)
        self.ixxx = tk.BooleanVar(value=True)
        self.kxxx = tk.BooleanVar(value=True)
        self.mxxx = tk.BooleanVar(value=True)
        self.oxxx = tk.BooleanVar(value=True)
        self.pxxx = tk.BooleanVar(value=True)
        self.qxxx = tk.BooleanVar(value=True)
        self.rxxx = tk.BooleanVar(value=True)
        self.uxxx = tk.BooleanVar(value=True)

        cxxx_check = ttk.Checkbutton(aquifers_frame, text="Cxxx", variable=self.cxxx)
        dxxx_check = ttk.Checkbutton(aquifers_frame, text="Dxxx", variable=self.dxxx)
        ixxx_check = ttk.Checkbutton(aquifers_frame, text="Ixxx", variable=self.ixxx)
        kxxx_check = ttk.Checkbutton(aquifers_frame, text="Kxxx", variable=self.kxxx)
        mxxx_check = ttk.Checkbutton(aquifers_frame, text="Mxxx", variable=self.mxxx)
        oxxx_check = ttk.Checkbutton(aquifers_frame, text="Oxxx", variable=self.oxxx)
        pxxx_check = ttk.Checkbutton(aquifers_frame, text="Pxxx", variable=self.pxxx)
        qxxx_check = ttk.Checkbutton(aquifers_frame, text="Qxxx", variable=self.qxxx)
        rxxx_check = ttk.Checkbutton(aquifers_frame, text="Rxxx", variable=self.rxxx)
        uxxx_check = ttk.Checkbutton(aquifers_frame, text="Uxxx", variable=self.uxxx)

        cxxx_check.grid(row=0, column=0, sticky=tk.W)
        dxxx_check.grid(row=1, column=0, sticky=tk.W)
        ixxx_check.grid(row=2, column=0, sticky=tk.W)
        kxxx_check.grid(row=3, column=0, sticky=tk.W)
        mxxx_check.grid(row=4, column=0, sticky=tk.W)
        oxxx_check.grid(row=5, column=0, sticky=tk.W)
        pxxx_check.grid(row=6, column=0, sticky=tk.W)
        qxxx_check.grid(row=7, column=0, sticky=tk.W)
        rxxx_check.grid(row=8, column=0, sticky=tk.W)
        uxxx_check.grid(row=9, column=0, sticky=tk.W)

        # Fill the Parameters frame.
        self.radius = tk.DoubleVar(value=3000)
        self.required = tk.IntVar(value=25)
        self.spacing = tk.DoubleVar(value=1000)
        self.firstyear = tk.IntVar(value=1871)
        self.lastyear = tk.IntVar(value=datetime.datetime.now().year)

        radius_text = ttk.Label(parameters_frame, text="radius")
        radius_sb = ttk.Spinbox(parameters_frame, textvariable=self.radius, from_=0, increment=100, to=1000000)

        required_text = ttk.Label(parameters_frame, text="required")
        required_sb = ttk.Spinbox(parameters_frame, textvariable=self.required, from_=0, increment=1, to=10000)

        spacing_text = ttk.Label(parameters_frame, text="spacing")
        spacing_sb = ttk.Spinbox(parameters_frame, textvariable=self.spacing, from_=0, increment=100, to=100000)

        firstyear_text = ttk.Label(parameters_frame, text="first year")
        firstyear_sb = ttk.Spinbox(parameters_frame, textvariable=self.firstyear)

        lastyear_text = ttk.Label(parameters_frame, text="last year")
        lastyear_sb = ttk.Spinbox(parameters_frame, textvariable=self.lastyear)

        radius_text.grid(row=0, column=0, sticky=tk.W, pady=2)
        radius_sb.grid(row=0, column=1, sticky=tk.W, pady=2)

        required_text.grid(row=1, column=0, sticky=tk.W, pady=2)
        required_sb.grid(row=1, column=1, sticky=tk.W, pady=2)

        spacing_text.grid(row=2, column=0, sticky=tk.W, pady=2)
        spacing_sb.grid(row=2, column=1, sticky=tk.W, pady=2)

        firstyear_text.grid(row=3, column=0, sticky=tk.W, pady=2)
        firstyear_sb.grid(row=3, column=1, sticky=tk.W, pady=2)

        lastyear_text.grid(row=4, column=0, sticky=tk.W, pady=2)
        lastyear_sb.grid(row=4, column=1, sticky=tk.W, pady=2)

        # Fill the buttons frame
        run_button = ttk.Button(buttons_frame, text="Run", command=self.run_button_pressed)
        save_button = ttk.Button(buttons_frame, text="Save", command=self.save_button_pressed)
        exit_button = ttk.Button(buttons_frame, text="Exit", command=self.exit_button_pressed)

        exit_button.pack(side=tk.BOTTOM, pady=2)
        save_button.pack(side=tk.BOTTOM, pady=2)
        run_button.pack(side=tk.BOTTOM, pady=2)


    def on_venue_type_select(self, event):
        selected_venue_type = self.venue_type.get()
        print(f"{selected_venue_type}")

        self.venue_city_frame.grid_forget()
        self.venue_township_frame.grid_forget()
        self.venue_county_frame.grid_forget()
        self.venue_watershed_frame.grid_forget()
        self.venue_subregion_frame.grid_forget()
        self.venue_neighborhood_frame.grid_forget()
        self.venue_frame_frame.grid_forget()

        if selected_venue_type == "City":
            self.venue_city_frame.grid(row=1, column=1, columnspan=2)
        elif selected_venue_type == "Township":
            self.venue_township_frame.grid(row=1, column=1, columnspan=2)
        elif selected_venue_type == "County":
            self.venue_county_frame.grid(row=1, column=1, columnspan=2)
        elif selected_venue_type == "Watershed":
            self.venue_watershed_frame.grid(row=1, column=1, columnspan=2)
        elif selected_venue_type == "Subregion":
            self.venue_subregion_frame.grid(row=1, column=1, columnspan=2)
        elif selected_venue_type == "Neighborhood":
            self.venue_neighborhood_frame.grid(row=1, column=1, columnspan=2)
        elif selected_venue_type == "Frame":
            self.venue_frame_frame.grid(row=1, column=1, columnspan=2)
        else:
            raise ValueError("Unknown venue type")

    def run_button_pressed(self):
        selected_venue_type = self.venue_type.get()
        if selected_venue_type == "City":
            self.venue_city_frame
        elif selected_venue_type == "Township":
            self.venue_township_frame
        elif selected_venue_type == "County":
            self.venue_county_frame
        elif selected_venue_type == "Watershed":
            self.venue_watershed_frame
        elif selected_venue_type == "Subregion":
            self.venue_subregion_frame
        elif selected_venue_type == "Neighborhood":
            self.venue_neighborhood_frame
        elif selected_venue_type == "Frame":
            self.venue_frame_frame
        else:
            raise ValueError("Unknown venue type")





        selected_aquifers = {

        }
        selected_parameters = {
            "radius": self.radius,
            "required": self.required,
            "spacing": self.spacing,
            "firstyear": self.firstyear,
            "lastyear": self.lastyear
        }
        self.run_callback(selected_venue, selected_aquifers, selected_parameters)

    def save_button_pressed(self):
        print("<save> button pressed")

    def exit_button_pressed(self):
        print("<exit> button pressed")
        self.destroy()
