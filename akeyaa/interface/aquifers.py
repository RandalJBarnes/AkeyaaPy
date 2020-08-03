"""Aquifers GUI"""

__author__ = "Randal J Barnes"
__version__ = "31 July 2020"

import numpy as np

import tkinter as tk
import tkinter.ttk as ttk

# The following is a complete list of all 4-character aquifer codes used in
# the Minnesota County Well index as of 1 January 2020. There are 10 groups
# by first letter: {C, D, I, K, M, O, P, Q, R, U}.
ALL_AQUIFERS = {
    "CAMB", "CECR", "CEMS", "CJDN", "CJDW", "CJMS", "CJSL", "CJTC", "CLBK",
    "CMFL", "CMRC", "CMSH", "CMTS", "CSLT", "CSLW", "CSTL", "CTCE", "CTCG",
    "CTCM", "CTCW", "CTLR", "CTMZ", "CWEC", "CWMS", "CWOC",
    "DCLP", "DCLS", "DCOG", "DCOM", "DCVA", "DCVL", "DCVU", "DEVO", "DPOG",
    "DPOM", "DSOG", "DSOM", "DSPL", "DWAP", "DWPR",
    "INDT",
    "KDNB", "KREG", "KRET",
    "MTPL",
    "ODCR", "ODGL", "ODPL", "ODUB", "OGCD", "OGCM", "OGDP", "OGPC", "OGPD",
    "OGPR", "OGSC", "OGSD", "OGSV", "OGVP", "OGWD", "OMAQ", "OMQD", "OMQG",
    "OPCJ", "OPCM", "OPCT", "OPCW", "OPDC", "OPGW", "OPNR", "OPOD", "OPSH",
    "OPSP", "OPVJ", "OPVL", "OPWR", "ORDO", "ORRV", "OSCJ", "OSCM", "OSCS",
    "OSCT", "OSPC", "OSTP", "OWIN",
    "PAAI", "PAAM", "PABD", "PABG", "PABK", "PACG", "PAEF", "PAES", "PAEY",
    "PAFL", "PAFR", "PAFV", "PAGR", "PAGU", "PAJL", "PAKG", "PALC", "PALG",
    "PALL", "PALP", "PALS", "PALT", "PALV", "PAMB", "PAMC", "PAMD", "PAMG",
    "PAML", "PAMR", "PAMS", "PAMT", "PAMU", "PAMV", "PANB", "PANL", "PANS",
    "PANU", "PAOG", "PAQF", "PASG", "PASH", "PASL", "PASM", "PASN", "PASR",
    "PAST", "PASZ", "PATL", "PAUD", "PAVC", "PAWB", "PCCR", "PCRG", "PCUU",
    "PEAG", "PEAL", "PEBC", "PEBI", "PEDN", "PEDQ", "PEFG", "PEFH", "PEFM",
    "PEGT", "PEGU", "PEHL", "PEIL", "PELF", "PELR", "PEMG", "PEML", "PEMN",
    "PEMU", "PEPG", "PEPK", "PEPP", "PEPZ", "PERB", "PERF", "PERV", "PESC",
    "PEST", "PESX", "PETR", "PEUD", "PEVT", "PEWR", "PEWT", "PEWV", "PMBB",
    "PMBE", "PMBI", "PMBL", "PMBM", "PMBO", "PMBR", "PMCV", "PMDA", "PMDC",
    "PMDE", "PMDF", "PMDL", "PMEP", "PMES", "PMFL", "PMGI", "PMGL", "PMHF",
    "PMHN", "PMHR", "PMLD", "PMMU", "PMNF", "PMNI", "PMNL", "PMNM", "PMNS",
    "PMPA", "PMRC", "PMSU", "PMTH", "PMUD", "PMUS", "PMVU", "PMWL", "PUDF",
    "QBAA", "QBUA", "QUUU", "QWTA",
    "RUUU",
    "UREG"
    }


class Aquifers(tk.Toplevel):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.title("Aquifers")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        ttk.Sizegrip(self).grid(row=1, column=2, sticky="SE")

        first_letters = []
        for aq in ALL_AQUIFERS:
            first_letters.append(aq[0])
        first_letters = np.unique(first_letters)

        self.tree = ttk.Treeview(self, show="tree")
        self.all_items = []
        for i, letter in enumerate(first_letters):
            iid = self.tree.insert("", "end", text=f"{letter}xxx", values=0)
            self.all_items.append(iid)

            for aq in ALL_AQUIFERS:
                if aq[0] == letter:
                    jid = self.tree.insert(iid, "end", text=aq, values=1)
                    self.all_items.append(jid)
        self.tree.grid(row=0, column=0, sticky="NSEW", padx=5, pady=5)

        self.scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="NSW")

        # Top right buttons.
        self.btn_frame = ttk.Frame(self, padding=10)
        self.btn_frame.grid(row=0, column=2)

        self.top_btn_frame = ttk.Frame(self.btn_frame)
        self.top_btn_frame.grid(row=0, column=0, pady=10)

        self.btn_all = ttk.Button(self.top_btn_frame, text="All", command=self.select_all)
        self.btn_all.grid(row=0, column=0)

        self.btn_none = ttk.Button(self.top_btn_frame, text="None", command=self.select_none)
        self.btn_none.grid(row=1, column=0)

        # Bottom right buttons
        self.bot_btn_frame = ttk.Frame(self.btn_frame)
        self.bot_btn_frame.grid(row=1, column=0, pady=10)

        self.btn_okay = ttk.Button(self.bot_btn_frame, text="OK", command=self.save_selection)
        self.btn_okay.grid(row=0, column=0)

        self.btn_cancel = ttk.Button(self.bot_btn_frame, text="Cancel", command=self.destroy)
        self.btn_cancel.grid(row=1, column=0)


    def select_all(self):
        self.tree.selection_set(self.all_items)


    def select_none(self):
        self.tree.selection_remove(self.all_items)


    def save_selection(self):
        self.parent.selected_aquifers = []
        for selection in self.tree.selection():
            item = self.tree.item(selection)
            if item["values"][0] > 0:
                self.parent.selected_aquifers.append(item["text"])
        self.destroy()
