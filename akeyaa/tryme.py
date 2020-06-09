# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 14:30:05 2020

@author: barne

"""

import os

import analyze as analyze
import archive as archive
import geology as geology
import parameters as parameters
import show as show
import venues as venues

from stopwatch import stopwatch


# =============================================================================
if __name__ == "__main__":
    # execute only if run as a script

    rolex = stopwatch()

    wash = venues.County(abbr="WASH")
    rolex.read("venues")

    geology.aquifers_by_venue(wash)
    rolex.read("geology")

    settings = parameters.Parameters(spacing=1000)
    results = analyze.by_venue(wash, settings)
    rolex.read("analyze")

    pklzfile = archive.saveme(wash, settings, results)
    rolex.read("archive")

    wash, settings, results = archive.loadme(pklzfile)
    rolex.read("load")

    show.by_venue(wash, results)
    rolex.read("show")

    os.remove(pklzfile)
    rolex.read("final")
