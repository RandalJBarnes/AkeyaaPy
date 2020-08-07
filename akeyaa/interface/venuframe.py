"""Smart Combobox"""

__author__ = "Randal J Barnes"
__version__ = "1 August 2020"

import tkinter as tk

class VenueFrame(tk.Frame):
    def __init__(self, parent, complete_list, contains=True):
        super().__init__(parent)

        self.parent = parent
        self.complete_list = complete_list
        self.contains = contains

        self.var_text = tk.StringVar()
        self.var_text.trace('w', self.on_change)

        self.entry = tk.Entry(self, textvariable=self.var_text)
        self.entry.pack(fill=tk.X, expand=0)

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=1)

        #listbox.bind('<Double-Button-1>', on_select)
        self.listbox.bind('<<ListboxSelect>>', self.on_select)
        self.listbox_update(self.complete_list)

    def on_change(self, *args):
        value = self.var_text.get()
        value = value.strip().lower()

        if value == '':
            data = self.complete_list
        else:
            data = []
            for item in self.complete_list:
                if self.contains:
                    if value in item.lower():
                        data.append(item)
                else:
                    if (len(item) >= len(value)) and (value == item[0:len(value)].lower()):
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

# --- main ---

if __name__ == "__main__":
    # execute only if run as a script
    test_list = [('apple', 1), ('banana', 2), ('Cranberry', 3), ('dogwood', 4), ('alpha', 5), ('Acorn', 6), ('Anise', 7), ('Strawberry', 8)]
    root = tk.Tk()
    scb = VenueFrame(root, test_list, contains=False)
    scb.pack(fill=tk.BOTH, expand=1)
    root.mainloop()
