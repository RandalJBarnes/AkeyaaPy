# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 14:30:05 2020

@author: barne
"""

if __name__ == "__main__":
    # execute only if run as a script

    from time import time
    start = time()

    import venues
    wash = venues.County(abbr='WASH')
    print(f"{time()-start:.2f} seconds.")

    import geology
    geology.aquifers_by_venue(wash)
    print(f"{time()-start:.2f} seconds.")

    import analyze
    settings = analyze.Settings(spacing=1000)
    results = analyze.by_venue(wash, settings)
    print(f"{time()-start:.2f} seconds.")

    import show
    show.results_by_venue(wash, results)
    print(f"{time()-start:.2f} seconds.")

    import archive
    pklzfile = archive.saveme(wash, settings, results)
    print(f"{time()-start:.2f} seconds.")
    archive.load_and_show_results(pklzfile)
    print(f"{time()-start:.2f} seconds.")

    import os
    os.remove(pklzfile)
    print(f"Total Elapsed time = {time()-start:.2f} seconds.")
