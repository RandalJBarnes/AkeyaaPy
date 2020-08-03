"""GDB Locations GUI"""

__author__ = "Randal J Barnes"
__version__ = "1 August 2020"

import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askdirectory

CWIGDB = "water_well_information.gdb"
CTUGDB = "bdry_mn_city_township_unorg.gdb"
CTYGDB = "bdry_counties_in_minnesota.gdb"
WBDGDB = "WBD_National_GDB.gdb"
STAGDB = "bdry_state.gdb"

class Locations(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.title("Settings")

        self.cwi_path = tk.StringVar()
        self.cwi_path.set(self.parent.cwi_path)

        self.ctu_path = tk.StringVar()
        self.ctu_path.set(self.parent.ctu_path)

        self.cty_path = tk.StringVar()
        self.cty_path.set(self.parent.cty_path)

        self.wbd_path = tk.StringVar()
        self.wbd_path.set(self.parent.wbd_path)

        self.sta_path = tk.StringVar()
        self.sta_path.set(self.parent.sta_path)

        self.req_frame = tk.LabelFrame(self, text="REQUIRED")
        self.opt_frame = tk.LabelFrame(self, text="OPTIONAL")
        self.btn_frame = tk.Frame(self)

        self.req_frame.grid(row=0, column=0, padx=5, pady=5)
        self.opt_frame.grid(row=1, column=0, padx=5, pady=5)
        self.btn_frame.grid(row=2, column=0, padx=5, pady=5, sticky="E")

        self.cwi_label = tk.Label(self.req_frame, text=CWIGDB, justify=tk.LEFT, anchor=tk.W)
        self.cwi_entry = tk.Entry(self.req_frame, textvariable=self.cwi_path, bg="white", width=60)
        self.cwi_btn = ttk.Button(self.req_frame, text="change", command=self.cwi_selector)

        self.cwi_label.grid(row=0, column=0, sticky="W", padx=5)
        self.cwi_entry.grid(row=1, column=0, sticky="W", padx=5)
        self.cwi_btn.grid(row=1, column=1, padx=5, pady=5)

        self.ctu_label = tk.Label(self.opt_frame, text=CTUGDB, justify=tk.LEFT)
        self.ctu_entry = tk.Entry(self.opt_frame, textvariable=self.ctu_path, bg="white", width=60)
        self.ctu_btn = ttk.Button(self.opt_frame, text="change", command=self.ctu_selector)

        self.ctu_label.grid(row=0, column=0, sticky="W", padx=5)
        self.ctu_entry.grid(row=1, column=0, sticky="W", padx=5)
        self.ctu_btn.grid(row=1, column=1, padx=5, pady=5)

        self.cty_label = tk.Label(self.opt_frame, text=CTYGDB, justify=tk.LEFT)
        self.cty_entry = tk.Entry(self.opt_frame, textvariable=self.cty_path, bg="white", width=60)
        self.cty_btn = ttk.Button(self.opt_frame, text="change", command=self.cty_selector)

        self.cty_label.grid(row=2, column=0, sticky="W", padx=5)
        self.cty_entry.grid(row=3, column=0, sticky="W", padx=5)
        self.cty_btn.grid(row=3, column=1, padx=5, pady=5)

        self.wbd_label = tk.Label(self.opt_frame, text=WBDGDB, justify=tk.LEFT)
        self.wbd_entry = tk.Entry(self.opt_frame, textvariable=self.wbd_path, bg="white", width=60)
        self.wbd_btn = ttk.Button(self.opt_frame, text="change", command=self.wbd_selector)

        self.wbd_label.grid(row=4, column=0, sticky="W", padx=5)
        self.wbd_entry.grid(row=5, column=0, sticky="W", padx=5)
        self.wbd_btn.grid(row=5, column=1, padx=5, pady=5)

        self.sta_label = tk.Label(self.opt_frame, text=STAGDB, justify=tk.LEFT)
        self.sta_entry = tk.Entry(self.opt_frame, textvariable=self.sta_path, bg="white", width=60)
        self.sta_btn = ttk.Button(self.opt_frame, text="change", command=self.sta_selector)

        self.sta_label.grid(row=6, column=0, sticky="W", padx=5)
        self.sta_entry.grid(row=7, column=0, sticky="W", padx=5)
        self.sta_btn.grid(row=7, column=1, padx=5, pady=5)

        self.btn_okay = ttk.Button(self.btn_frame, text="OK", command=self.save_settings)
        self.btn_okay.grid(row=0, column=0, sticky="E")

        self.btn_cancel = ttk.Button(self.btn_frame, text="Cancel", command=self.destroy)
        self.btn_cancel.grid(row=0, column=1, sticky="E")

    def cwi_selector(self):
        folder = askdirectory(parent=self, mustexist=True, title=CWIGDB)
        if folder is not None:
            self.cwi_path.set(folder)

    def ctu_selector(self):
        folder = askdirectory(parent=self, mustexist=True, title=CTUGDB)
        if folder is not None:
            self.ctu_path.set(folder)

    def cty_selector(self):
        folder = askdirectory(parent=self, mustexist=True, title=CTYGDB)
        if folder is not None:
            self.cty_path.set(folder)

    def wbd_selector(self):
        folder = askdirectory(parent=self, mustexist=True, title=WBDGDB)
        if folder is not None:
            self.wbd_path.set(folder)

    def sta_selector(self):
        folder = askdirectory(parent=self, mustexist=True, title=STAGDB)
        if folder is not None:
            self.sta_path.set(folder)


    def save_settings(self):
        def shorten(str):
            str = str.strip()
            if len(str) > 0:
                return str
            else:
                return None

        self.parent.cwi_path = shorten(self.cwi_path.get())
        self.parent.ctu_path = shorten(self.ctu_path.get())
        self.parent.cty_path = shorten(self.cty_path.get())
        self.parent.wbd_path = shorten(self.wbd_path.get())
        self.parent.sta_path = shorten(self.sta_path.get())
        self.parent.save_configuration()

        self.destroy()
