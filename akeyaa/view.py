"""Implement the graphical user interface, View class, for AkeyaaPy.

This file contains the entire graphical user interface for AkeyaaPy. This GUI
is all built on tkinter, which is the default python GUI.

"""

import datetime
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, filedialog

__author__ = "Randal J Barnes"
__version__ = "24 August 2020"


class View(tk.Tk):
    def __init__(self, venue_data, run_callback, save_callback):
        super().__init__()

        # Initialize.
        self.enumerated_venue_data = {
            "City": [(venue, index) for index, venue in enumerate(venue_data["city_list"])],
            "Township": [(venue, index) for index, venue in enumerate(venue_data["township_list"])],
            "County": [(venue, index) for index, venue in enumerate(venue_data["county_list"])],
            "Watershed": [(venue, index) for index, venue in enumerate(venue_data["watershed_list"])],
            "Subregion": [(venue, index) for index, venue in enumerate(venue_data["subregion_list"])]
        }
        self.venue_codes = {
            "City": "GNIS",
            "Township": "GNIS",
            "County": "FIPS",
            "Watershed": "HUC10",
            "Subregion": "HUC8"
        }

        self.run_callback = run_callback
        self.save_callback = save_callback

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
        self.venue_type = tk.StringVar(value=None)

        venue_label = ttk.Label(venue_frame, text="type")
        venue_cb = ttk.Combobox(
            venue_frame,
            state="readonly",
            textvariable=self.venue_type,
            values=venue_types
        )
        venue_cb.bind("<<ComboboxSelected>>", self.on_venue_type_select)

        venue_label.grid(row=0, column=0, sticky=tk.W)
        venue_cb.grid(row=0, column=1, sticky=tk.W)

        # Fill the Selection frame (a sub-frame in the Venue frame).
        self.selection_frame = ttk.Frame(venue_frame)

        self.selection_index = None
        self.enumerated_venue_list = None

        self.selection_text = tk.StringVar()
        self.selection_text.trace("w", self.on_change_selection_text)

        selection_label = ttk.Label(self.selection_frame, text="name")
        entry = ttk.Entry(self.selection_frame, textvariable=self.selection_text, width=33)
        entry.focus_set()

        # Fix for setting text colour for Tkinter 8.6.9
        # From: https://core.tcl.tk/tk/info/509cafafae
        style = ttk.Style()
        style.map(
            "Treeview",
            background=[elm for elm in style.map("Treeview", query_opt="background") if elm[:2] != ('!disabled', '!selected')]
        )

        self.selection_tree = ttk.Treeview(self.selection_frame, columns=("#1"), selectmode="browse")
        self.selection_tree.heading("#0", text="Name")
        self.selection_tree.heading("#1", text="Code")
        self.selection_tree.column("#0", stretch=tk.YES)
        self.selection_tree.column("#1", width=100)

        self.selection_tree.bind("<<TreeviewSelect>>", self.on_selection)
        self.selection_tree.tag_configure("current", background="orange")

        # entry.pack(fill=tk.X, expand=0)
        # self.selection_tree.pack(fill=tk.BOTH, expand=1)

        selection_label.grid(row=0, column=0)
        entry.grid(row=0, column=1, sticky=tk.W)
        self.selection_tree.grid(row=1, column=1, sticky=tk.W)

        # Fill the Neighborhood frame (a sub-frame in the Venue frame).
        self.neighborhood_frame = ttk.Frame(venue_frame)

        self.neighborhood_easting = tk.DoubleVar(value=481738.99)               # Civil Engineering Building
        self.neighborhood_northing = tk.DoubleVar(value=4980337.72)             # Univeristy of Minnesota
        self.neighborhood_radius = tk.DoubleVar(value=10000)                    # Go Gophers!

        easting_text = ttk.Label(self.neighborhood_frame, text="easting")
        easting_sb = ttk.Spinbox(
            self.neighborhood_frame,
            textvariable=self.neighborhood_easting,
            from_=189783, increment=100, to=761654                              # min & max for MN
        )

        northing_text = ttk.Label(self.neighborhood_frame, text="northing")
        northing_sb = ttk.Spinbox(
            self.neighborhood_frame,
            textvariable=self.neighborhood_northing,
            from_=4816309, increment=100, to=5472347                            # min & max for MN
        )

        radius_text = ttk.Label(self.neighborhood_frame, text="radius")
        radius_sb = ttk.Spinbox(
            self.neighborhood_frame,
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
        self.frame_frame = ttk.Frame(venue_frame)

        self.frame_minimum_easting = tk.DoubleVar(value=481738.99 - 10000)      # Civil Engineering Building
        self.frame_maximum_easting = tk.DoubleVar(value=481738.99 + 10000)      # Univeristy of Minnesota
        self.frame_minimum_northing = tk.DoubleVar(value=4980337.72 - 10000)    # Go Gophers!
        self.frame_maximum_northing = tk.DoubleVar(value=4980337.72 + 10000)

        easting_text = tk.Label(self.frame_frame, text="easting")
        northing_text = tk.Label(self.frame_frame, text="northing")
        minimum_text = tk.Label(self.frame_frame, text="minimum")
        maximum_text = tk.Label(self.frame_frame, text="maximum")

        minimum_easting_sb = tk.Spinbox(
            self.frame_frame,
            textvariable=self.frame_minimum_easting,
            from_=189783, increment=100, to=761654                              # min & max for MN
        )

        maximum_easting_sb = tk.Spinbox(
            self.frame_frame,
            textvariable=self.frame_maximum_easting,
            from_=189783, increment=100, to=761654                              # min & max for MN
        )

        minimum_northing_sb = tk.Spinbox(
            self.frame_frame,
            textvariable=self.frame_minimum_northing,
            from_=4816309, increment=100, to=5472347                            # min & max for MN
        )

        maximum_northing_sb = tk.Spinbox(
            self.frame_frame,
            textvariable=self.frame_maximum_northing,
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
        radius_sb = ttk.Spinbox(parameters_frame, textvariable=self.radius,
                                from_=1, increment=100, to=1000000)

        required_text = ttk.Label(parameters_frame, text="required")
        required_sb = ttk.Spinbox(parameters_frame, textvariable=self.required,
                                  from_=6, increment=1, to=10000)

        spacing_text = ttk.Label(parameters_frame, text="spacing")
        spacing_sb = ttk.Spinbox(parameters_frame, textvariable=self.spacing,
                                 from_=1, increment=100, to=100000)

        firstyear_text = ttk.Label(parameters_frame, text="first year")
        firstyear_sb = ttk.Spinbox(parameters_frame, textvariable=self.firstyear,
                                   from_=1871, increment=1, to=datetime.datetime.now().year)

        lastyear_text = ttk.Label(parameters_frame, text="last year")
        lastyear_sb = ttk.Spinbox(parameters_frame, textvariable=self.lastyear,
                                  from_=1871, increment=1, to=datetime.datetime.now().year)

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
        self.run_button = ttk.Button(buttons_frame, text="Run", command=self.run_button_pressed)
        self.save_button = ttk.Button(buttons_frame, text="Save", command=self.save_button_pressed, state=tk.DISABLED)
        self.about_button = ttk.Button(buttons_frame, text="About", command=self.about_button_pressed)
        self.exit_button = ttk.Button(buttons_frame, text="Exit", command=self.exit_button_pressed)

        self.exit_button.pack(side=tk.BOTTOM, pady=2)
        self.about_button.pack(side=tk.BOTTOM, pady=2)
        self.save_button.pack(side=tk.BOTTOM, pady=2)
        self.run_button.pack(side=tk.BOTTOM, pady=2)


    def on_venue_type_select(self, event):
        self.selection_frame.grid_forget()
        self.neighborhood_frame.grid_forget()
        self.frame_frame.grid_forget()

        if self.venue_type.get() == "Neighborhood":
            self.neighborhood_frame.grid(row=1, column=1, columnspan=3)
        elif self.venue_type.get() == "Frame":
            self.frame_frame.grid(row=1, column=1, columnspan=3)
        else:
            self.selection_name = None
            self.selection_code = None
            self.selection_index = None

            self.selection_frame.grid(row=1, column=1, columnspan=3)
            self.enumerated_venue_list = self.enumerated_venue_data[self.venue_type.get()]
            self.selection_text.set("")
            self.selection_tree.heading("#1", text=self.venue_codes[self.venue_type.get()])
            self.selection_tree_update(self.enumerated_venue_list)

    def on_change_selection_text(self, *args):
        value = self.selection_text.get()
        value = value.strip().lower()
        if value == "":
            venues = self.enumerated_venue_list
        else:
            venues = []
            for row in self.enumerated_venue_list:
                if value in row[0][0].lower():
                    venues.append(row)
        self.selection_tree_update(venues)

    def selection_tree_update(self, venues):
        self.selection_tree.delete(*self.selection_tree.get_children())
        for row in venues:
            if row[1] == self.selection_index:
                self.selection_tree.insert("", "end", text=row[0][0], values=(f"{row[0][1]}", row[1]), tags="current")
            else:
                self.selection_tree.insert("", "end", text=row[0][0], values=(f"{row[0][1]}", row[1]))

    def on_selection(self, event):
        selection = self.selection_tree.selection()
        item = self.selection_tree.item(selection)

        self.selection_name = item["text"]
        self.selection_code = item["values"][0]
        self.selection_index = item["values"][1]

        self.selection_text.set(item["text"])

    def run_button_pressed(self):
        valid_run = True

        # Set up the venue.
        try:
            if self.venue_type.get() == "Neighborhood":
                selected_venue = {
                    "type": "Neighborhood",
                    "name": "Neighborhood",
                    "easting": self.neighborhood_easting.get(),
                    "northing": self.neighborhood_northing.get(),
                    "radius": self.neighborhood_radius.get()
                }
            elif self.venue_type.get() == "Frame":
                selected_venue = {
                    "type": "Frame",
                    "name": "Frame",
                    "minimum_easting": self.frame_minimum_easting.get(),
                    "maximum_easting": self.frame_maximum_easting.get(),
                    "minimum_northing": self.frame_minimum_northing.get(),
                    "maximum_northing": self.frame_maximum_northing.get()
                }
            elif self.venue_type.get() in ["City", "Township", "County", "Watershed", "Subregion"]:
                selected_venue = {
                    "type": self.venue_type.get(),
                    "name": self.selection_name,
                    "code": self.selection_code,
                    "index": self.selection_index
                }
            else:
                raise NotImplementedError

        except (NotImplementedError, TypeError):
            valid_run = False
            messagebox.showerror(title="AkeyaPy", message="You must select a venue first.")

        # Set up the aquifers
        selected_aquifers = ""
        if self.cxxx.get():
            selected_aquifers += "C"
        if self.dxxx.get():
            selected_aquifers += "D"
        if self.ixxx.get():
            selected_aquifers += "I"
        if self.kxxx.get():
            selected_aquifers += "K"
        if self.mxxx.get():
            selected_aquifers += "M"
        if self.oxxx.get():
            selected_aquifers += "O"
        if self.pxxx.get():
            selected_aquifers += "P"
        if self.qxxx.get():
            selected_aquifers += "Q"
        if self.rxxx.get():
            selected_aquifers += "R"
        if self.uxxx.get():
            selected_aquifers += "U"

        if not selected_aquifers:
            valid_run = False
            messagebox.showerror(title="AkeyaPy", message="At least one aquifer class must be selected.")

        # Set up the parameters
        selected_parameters = {
            "radius": self.radius.get(),
            "required": self.required.get(),
            "spacing": self.spacing.get(),
            "firstyear": self.firstyear.get(),
            "lastyear": self.lastyear.get()
        }
        if selected_parameters["firstyear"] > selected_parameters["lastyear"]:
            valid_run = False
            messagebox.showerror(title="AkeyaPy", message="The first year must be less than or equal to last year.")

        # Run the model
        if valid_run:
            self.run_callback(selected_venue, selected_aquifers, selected_parameters)
            self.save_button["state"] = tk.NORMAL

    def save_button_pressed(self):
        print("<save> button pressed")
        filename = filedialog.asksaveasfilename(defaultextension="csv")
        if filename:
            self.save_callback(filename)

    def about_button_pressed(self):
        messagebox.showinfo(
            title="AkeyaaPy",
            message="AkeyaaPy 0.9\n16 August 2020\nUniversity of Minnesota"
        )

    def exit_button_pressed(self):
        print("<exit> button pressed")
        self.destroy()
