"""Venue widget = smart Combobox"""

__author__ = "Randal J Barnes"
__version__ = "13 August 2020"

import tkinter as tk
import tkinter.ttk as ttk

class VenueWidget(ttk.Frame):
    def __init__(self, parent, venue_list):
        super().__init__(parent)

        self.parent = parent
        self.enumerated_venue_list = [(venue, index) for index, venue in enumerate(venue_list)]

        self.var_text = tk.StringVar()
        self.var_text.trace('w', self.on_change)

        self.entry = ttk.Entry(self, textvariable=self.var_text)
        self.entry.focus_set()
        self.entry.pack(fill=tk.X, expand=0)

        self.tree = ttk.Treeview(self, columns=("Code"), selectmode="browse")
        self.tree.heading('#0', text='Name')
        self.tree.heading('#1', text='Code')
        self.tree.column('#0', stretch=tk.YES)
        self.tree.column('#1', width=100)
        self.tree.pack(fill=tk.BOTH, expand=1)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree_update(self.enumerated_venue_list)

    def on_change(self, *args):
        value = self.var_text.get()
        value = value.strip().lower()
        if value == '':
            venues = self.enumerated_venue_list
        else:
            venues = []
            for row in self.enumerated_venue_list:
                if value in row[0][0].lower():
                    venues.append(row)
        self.tree_update(venues)

    def tree_update(self, venues):
        self.tree.delete(*self.tree.get_children())
        for row in venues:
            self.tree.insert('', 'end', text=row[0][0], values=(f"{row[0][1]}", row[1]))

    def on_select(self, event):
        selection = self.tree.selection()
        item = self.tree.item(selection)
        self.var_text.set(item["text"])
