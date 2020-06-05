# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 14:30:05 2020

@author: barne
"""

# -----------------------------------------------------------------------------
import time
class stopwatch():

    def __init__(self):
        self.start = time.time()
        self.prior = self.start

    def read(self, label):
        now = time.time()
        elapsed = now - self.start
        split = now - self.prior
        self.prior = now
        print(f"{label:8s}: {split:7.2f}, {elapsed:7.2f} seconds")


# =============================================================================
if __name__ == "__main__":
    # execute only if run as a script

    rolex = stopwatch()

    import venues
    wash = venues.County(abbr='WASH')
    rolex.read('venues')

    import geology
    geology.aquifers_by_venue(wash)
    rolex.read('geology')

    import analyze
    settings = analyze.Settings(spacing=1000)
    results = analyze.by_venue(wash, settings)
    rolex.read('analyze')

    import show
    show.results_by_venue(wash, results)
    rolex.read('show')

    import archive
    pklzfile = archive.saveme(wash, settings, results)
    rolex.read('archive')

    archive.load_and_show_results(pklzfile)
    rolex.read('load')

    import os
    os.remove(pklzfile)
    rolex.read('final')
