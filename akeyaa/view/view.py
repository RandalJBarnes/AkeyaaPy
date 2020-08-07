"""Implement the View class in the adapted MVC design pattern for AkeyaaPy."""

import tkinter as tk
import tkinter.ttk as ttk

from akeyaa.view.parameters_dialog import ParametersDialog
from akeyaa.view.venue_dialog import VenueDialog

__author__ = "Randal J Barnes"
__version__ = "07 August 2020"


class View(tk.Tk):
    def __init__(self, parameters, venue_data):
        super().__init__()

        # Initialize.
        self.parameters = parameters
        self.venue_data = venue_data
        self.venue = None

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


    def start(self):
        self.mainloop()

    def show_parameters_dialog(self):
        dialog = ParametersDialog(self)

    def show_city_dialog(self):
        city_list = self.venue_data["city_list"]
        choices = [row[0] for row in city_list]
        dialog = VenueDialog(self, "City", choices)

    def show_township_dialog(self):
        township_list = self.venue_data["township_list"]
        choices = [row[0] for row in township_list]
        dialog = VenueDialog(self, "Township", choices)

    def show_county_dialog(self):
        county_list = self.venue_data["county_list"]
        choices = [row[0] for row in county_list]
        dialog = VenueDialog(self, "County", choices)

    def show_watershed_dialog(self):
        watershed_list = self.venue_data["watershed_list"]
        choices = [row[0] for row in watershed_list]
        dialog = VenueDialog(self, "Watershed", choices)

    def show_subregion_dialog(self):
        subregion_list = self.venue_data["subregion_list"]
        choices = [row[0] for row in subregion_list]
        dialog = VenueDialog(self, "Subregion", choices)

    def show_neighborhood_dialog(self):
        print("Neighborhood dialog")

    def show_frame_dialog(self):
        print("Frame dialog")

    def execute_akeyaa(self):
        print("EXECUTE AKEYAA")
        print(f"{self.venue}")
        print(f"{self.parameters}")
