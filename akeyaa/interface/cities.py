"""Parameters GUI"""

__author__ = "Randal J Barnes"
__version__ = "02 August 2020"

import tkinter as tk
import tkinter.ttk as ttk
from akeyaa.interface.smartcombobox import SmartCombobox

class Cities(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
        self.title("Cities")

        self.scb_frame = SmartCombobox(self, self.parent.city_list)
        self.scb_frame.grid(row=0, column=0, padx=5, pady=5)

        self.btn_frame = tk.Frame(self)
        self.btn_frame.grid(row=1, column=0, padx=5, pady=5, sticky="E")

        self.btn_okay = ttk.Button(self.btn_frame, text="OK", command=self.save_selection)
        self.btn_okay.grid(row=0, column=0, sticky="E")

        self.btn_cancel = ttk.Button(self.btn_frame, text="Cancel", command=self.destroy)
        self.btn_cancel.grid(row=0, column=1, sticky="E")


    def save_selection(self):
        self.parent.city = self.scb_frame.selection
        self.destroy()
