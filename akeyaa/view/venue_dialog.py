"""Smart Combobox"""

__author__ = "Randal J Barnes"
__version__ = "07 August 2020"

import tkinter as tk
import tkinter.ttk as ttk

class VenueDialog(tk.Toplevel):
    def __init__(self, parent, title_str, choices):
        super().__init__(parent)

        self.parent = parent
        self.parent.wm_attributes("-disabled", True)        # Make the dialog modal

        self.venue = None
        self.choices = choices

        self.title(title_str)

        self.top_frame = tk.Frame(self)
        self.btn_frame = tk.Frame(self)
        self.map_frame = tk.Frame(self)

        self.top_frame.grid(row=0, column=0, padx=5, pady=5)
        self.btn_frame.grid(row=1, column=1, padx=5, pady=5, sticky="E")
        self.map_frame.grid(row=0, column=1)

        self.var_text = tk.StringVar()
        self.var_text.trace('w', self.on_change)

        self.entry = tk.Entry(self.top_frame, textvariable=self.var_text)
        self.entry.pack(fill=tk.X, expand=0)

        self.listbox = tk.Listbox(self.top_frame)
        self.listbox.pack(fill=tk.BOTH, expand=1)

        #listbox.bind('<Double-Button-1>', on_select)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox_update(self.choices)

        self.btn_okay = ttk.Button(self.btn_frame, text="OK", command=self.okay)
        self.btn_okay.grid(row=0, column=0, sticky="E")

        self.btn_cancel = ttk.Button(self.btn_frame, text="Cancel", command=self.cancel)
        self.btn_cancel.grid(row=0, column=1, sticky="E")

    def on_change(self, *args):
        value = self.var_text.get()
        value = value.strip().lower()

        if value == '':
            data = self.choices
        else:
            data = []
            for item in self.choices:
                if value in item.lower():
                    data.append(item)
        self.listbox_update(data)

    def listbox_update(self, data):
        self.listbox.delete(0, 'end')
        data = sorted(data, key=str.lower)
        for item in data:
            self.listbox.insert('end', item)

    def on_select(self, event):
        # display element selected on list'
        self.selection = event.widget.get(event.widget.curselection())
        self.var_text.set(self.selection)

    def okay(self):
        self.parent.venue = self.var_text.get()
        self.parent.wm_attributes("-disabled", False)
        self.destroy()

    def cancel(self):
        self.parent.wm_attributes("-disabled", False)
        self.destroy()




# --- main ---

if __name__ == "__main__":
    # execute only if run as a script
    test_list = ['apple', 'banana', 'Cranberry', 'dogwood', 'alpha', 'Acorn', 'Anise', 'Strawberry']
    test_list_2 = [('apple', 1), ('banana', 2), ('Cranberry', 3), ('dogwood', 4), ('alpha', 5), ('Acorn', 6), ('Anise', 7), ('Strawberry', 8)]

    root = tk.Tk()
    scb = VenueDialog(root, "Venue Dialog", test_list)
    root.mainloop()
