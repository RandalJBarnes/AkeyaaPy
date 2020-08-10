"""Implement the View class in the adapted MVC design pattern for AkeyaaPy."""

import tkinter as tk
import tkinter.ttk as ttk

from akeyaa.view.parameters_dialog import ParametersDialog
from akeyaa.view.venue_dialog import VenueDialog
from akeyaa.view.neighborhood_dialog import NeighborhoodDialog
from akeyaa.view.frame_dialog import FrameDialog

__author__ = "Randal J Barnes"
__version__ = "09 August 2020"


class View(tk.Tk):
    def __init__(self, parameters, venue_data, run_callback):
        super().__init__()

        # Initialize.
        self.parameters = parameters
        self.venue_data = venue_data
        self.venue = {"type" : None}
        self.run_callback = run_callback

        # Main window.
        self.title("AkeyaaPy")
        self.geometry("800x800")

        # Main menu.
        main_menu = tk.Menu(self)

        venu_menu = tk.Menu(main_menu, tearoff=0)
        venu_menu.add_command(label="City", command=self.show_city_dialog)
        venu_menu.add_command(label="Township", command=self.show_township_dialog)
        venu_menu.add_command(label="County", command=self.show_county_dialog)
        venu_menu.add_separator()
        venu_menu.add_command(label="Watershed", command=self.show_watershed_dialog)
        venu_menu.add_command(label="Subregion", command=self.show_subregion_dialog)
        venu_menu.add_separator()
        venu_menu.add_command(label="Neighborhood", command=self.show_neighborhood_dialog)
        venu_menu.add_command(label="Frame", command=self.show_frame_dialog)

        main_menu.add_cascade(label="Venues", menu=venu_menu)
        main_menu.add_command(label="Parameters", command=self.show_parameters_dialog)
        main_menu.add_command(label="Run", command=self.execute_akeyaa)
        main_menu.add_command(label="Exit", command=self.destroy)

        self.config(menu=main_menu)

        # Notebooks
        nb = ttk.Notebook(self)
        nb.pack()

        f1 = tk.Frame(nb)
        nb.add(f1, text="Geology")

        f2 = tk.Frame(nb)
        nb.add(f2, text="Count")

        f3 = tk.Frame(nb)
        nb.add(f3, text="Local Head")

        f4 = tk.Frame(nb)
        nb.add(f4, text="Local Gradient")

        f5 = tk.Frame(nb)
        nb.add(f5, text="Laplacian Zscore")

        f6 = tk.Frame(nb)
        nb.add(f6, text="Flow Direction")

        nb.select(f1)
        nb.enable_traversal()

    def show_parameters_dialog(self):
        dialog = ParametersDialog(self)

    def show_city_dialog(self):
        city_list = self.venue_data["city_list"]
        dialog = VenueDialog(self, "City", city_list)

    def show_township_dialog(self):
        township_list = self.venue_data["township_list"]
        dialog = VenueDialog(self, "Township", township_list)

    def show_county_dialog(self):
        county_list = self.venue_data["county_list"]
        dialog = VenueDialog(self, "County", county_list)

    def show_watershed_dialog(self):
        watershed_list = self.venue_data["watershed_list"]
        dialog = VenueDialog(self, "Watershed", watershed_list)

    def show_subregion_dialog(self):
        subregion_list = self.venue_data["subregion_list"]
        dialog = VenueDialog(self, "Subregion", subregion_list)

    def show_neighborhood_dialog(self):
        dialog = NeighborhoodDialog(self)

    def show_frame_dialog(self):
        dialog = FrameDialog(self)

    def execute_akeyaa(self):
        self.run_callback(self.venue, self.parameters)
