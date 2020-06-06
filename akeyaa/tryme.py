# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 14:30:05 2020

@author: barne

"""

import os

import analyze
import archive
import geology
import show
import venues

from stopwatch import stopwatch


# =============================================================================
if __name__ == "__main__":
    # execute only if run as a script

    rolex = stopwatch()

    wash = venues.County(abbr="WASH")
    rolex.read("venues")

    geology.aquifers_by_venue(wash)
    rolex.read("geology")

    settings = analyze.Settings(spacing=1000)
    results = analyze.by_venue(wash, settings)
    rolex.read("analyze")

    show.results_by_venue(wash, results)
    rolex.read("show")

    pklzfile = archive.saveme(wash, settings, results)
    rolex.read("archive")

    archive.load_and_show_results(pklzfile)
    rolex.read("load")

    os.remove(pklzfile)
    rolex.read("final")
