# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 14:30:05 2020

@author: barne
"""

if __name__ == "__main__":
    # execute only if run as a script

    import time
    start = time.time()

    import venues
    wash = venues.County(abbr='WASH')

    import geology
    geology.aquifers_by_venue(wash)

    import analyze
    settings = analyze.Settings(spacing=750)
    results = analyze.by_venue(wash, settings)

    import show
    show.results_by_venue(wash, results)

    import archive
    pklzfile = archive.saveme(wash, settings, results)
    archive.load_and_show_results(pklzfile)

    import os
    os.remove(pklzfile)

    print(f"Total Elapsed time = {time.time()-start:.2f} seconds.")