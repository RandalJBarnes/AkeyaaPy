"""Root GUI"""

__author__ = "Randal J Barnes"
__version__ = "1 August 2020"

import datetime
import tkinter as tk

from akeyaa.view.parameters_dialog import Parameters
from akeyaa.interface.aquifers import Aquifers
from akeyaa.interface.locations import Locations
from akeyaa.interface.cities import Cities

class Root(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Akeyaa")
        self.geometry("800x800")

        # parameters
        self.radius = 2000
        self.required = 25
        self.spacing = 1000
        self.firstyear = 1960
        self.lastyear = datetime.datetime.now().year

        # aquifers
        self.selected_aquifers = []

        # root menu
        root_menu = tk.Menu(self)

        file_menu = tk.Menu(root_menu, tearoff=0)
        file_menu.add_command(label="New file")
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Save as...")
        root_menu.add_cascade(label="File", menu=file_menu)

        set_menu = tk.Menu(root_menu, tearoff=0)
        set_menu.add_command(label="GDB Locations", command=self.show_locations_selector)
        set_menu.add_command(label="Default Values")
        root_menu.add_cascade(label="Settings", menu=set_menu)

        root_menu.add_command(label="Parameters", command=self.show_parameters_selector)

        root_menu.add_command(label="Aquifers", command=self.show_aquifers_selector)

        venu_menu = tk.Menu(root_menu, tearoff=0)
        venu_menu.add_command(label="City", command=self.show_city_selector)
        venu_menu.add_command(label="Township")
        venu_menu.add_command(label="County")
        venu_menu.add_separator()
        venu_menu.add_command(label="Watershed")
        venu_menu.add_command(label="Subregion")
        venu_menu.add_separator()
        venu_menu.add_command(label="Neighborhood")
        venu_menu.add_command(label="Frame")
        venu_menu.add_command(label="Patch")
        root_menu.add_cascade(label="Venues", menu=venu_menu)

        root_menu.add_command(label="Run", command=self.run_akeyaa)
        root_menu.add_command(label="Quit", command=self.destroy)

        self.config(menu=root_menu)


    def show_locations_selector(self):
        locations_selector = Locations(self)

    def show_parameters_selector(self):
        parameters_selector = Parameters(self)

    def show_aquifers_selector(self):
        aquifers_selector = Aquifers(self)

    def show_city_selector(self):
        city_selector = Cities(self)

    def run_akeyaa(self):
        if len(self.selected_aquifers) > 0:
            for aq in self.selected_aquifers:
                print(aq)
        else:
            print("No aquifers were selected.")
