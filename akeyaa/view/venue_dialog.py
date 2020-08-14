"""Smart Combobox"""

__author__ = "Randal J Barnes"
__version__ = "11 August 2020"

import tkinter as tk
import tkinter.ttk as ttk

class VenueDialog(tk.Toplevel):
    def __init__(self, parent, venue_type, venue_list):
        super().__init__(parent)

        self.parent = parent
        self.parent.wm_attributes("-disabled", True)        # Make the dialog modal
        self.enumerated_venue_list = [(venue, index) for index, venue in enumerate(venue_list)]

        self.selected_venue = {
            "type" : venue_type,
            "name" : None,
            "code" : None,
            "index" : None
        }

        self.title(venue_type)

        self.top_frame = tk.Frame(self)
        self.btn_frame = tk.Frame(self)

        self.top_frame.grid(row=0, column=0, padx=5, pady=5)
        self.btn_frame.grid(row=1, column=0, padx=5, pady=5, sticky="E")

        self.var_text = tk.StringVar()
        self.var_text.trace('w', self.on_change)

        self.entry = tk.Entry(self.top_frame, textvariable=self.var_text)
        self.entry.focus_set()
        self.entry.pack(fill=tk.X, expand=0)

        self.tree = ttk.Treeview(self.top_frame, columns=("ID"), selectmode="browse")
        self.tree.heading('#0', text='Name')
        self.tree.heading('#1', text='Code')
        self.tree.column('#0', stretch=tk.YES)
        self.tree.column('#1', width=100)

        self.tree.pack(fill=tk.BOTH, expand=1)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree_update(self.enumerated_venue_list)


        # Setup the button frame.
        self.btn_okay = ttk.Button(self.btn_frame, text="OK", command=self.okay)
        self.btn_okay["state"] = tk.DISABLED
        self.btn_okay.grid(row=0, column=0, sticky="E")

        self.btn_cancel = ttk.Button(self.btn_frame, text="Cancel", command=self.cancel)
        self.btn_cancel.grid(row=0, column=1, sticky="E")

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

        self.selected_venue["name"] = None
        self.selected_venue["code"] = None
        self.selected_venue["index"] = None

        self.btn_okay["state"] = tk.DISABLED

    def tree_update(self, venues):
        self.tree.delete(*self.tree.get_children())
        for row in venues:
            self.tree.insert('', 'end', text=row[0][0], values=(f"{row[0][1]}", row[1]))

    def on_select(self, event):
        selection = self.tree.selection()
        item = self.tree.item(selection)
        self.var_text.set(item["text"])

        self.selected_venue["name"] = item["text"]
        self.selected_venue["code"] = item["values"][0]
        self.selected_venue["index"] = item["values"][1]

        self.btn_okay["state"] = tk.NORMAL

    def okay(self):
        self.parent.selected_venue = self.selected_venue
        self.parent.wm_attributes("-disabled", False)
        self.destroy()

    def cancel(self):
        self.parent.wm_attributes("-disabled", False)
        self.destroy()
