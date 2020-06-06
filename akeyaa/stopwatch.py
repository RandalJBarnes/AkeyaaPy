"""A simple stopwatch.

Class
-----
stopwatch

Author
------
Dr. Randal J. Barnes
Department of Civil, Environmental, and Geo- Engineering
University of Minnesota

Version
-------
06 June 2020

"""
import time

class stopwatch():
    """A simple stopwatch.

    Attributes
    ----------
    start : float
        The start time.

    prior : float
        The time at the beginning of the split.

    Methods
    -------
    __init__(self)
        Initialize and start the stopwatch.

    read(self, label)
        Print out total elapsed time and split time.

    reset(self)
        Reset the start time.
    """

    def __init__(self):
        self.start = time.time()
        self.prior = self.start

    def read(self, label):
        now = time.time()
        elapsed = now - self.start
        split = now - self.prior
        self.prior = now
        print(f"{label:8s}: {split:7.2f}, {elapsed:7.2f} seconds")

    def reset(self):
        self.start = time.time()
        self.prior = self.start
