# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 14:30:05 2020

@author: barne

"""

import os

import akeyaa.analyze as analyze
import akeyaa.archive as archive
import akeyaa.geology as geology
import akeyaa.parameters as parameters
import akeyaa.show as show
import akeyaa.venues as venues
from akeyaa.wells import Wells

from akeyaa.stopwatch import stopwatch

def main():
    rolex = stopwatch()

    Wells.initialize()
    rolex.read("initial")

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


# =============================================================================
if __name__ == "__main__":
    # execute only if run as a script
    main()