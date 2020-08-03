"""My simple stopwatch."""

import time

__author__ = "Randal J Barnes"
__version__ = "24 July 2020"


class stopwatch:
    """A simple stopwatch class.

    Attributes
    ----------
    start : float
        The start time.

    prior : float
        The time at the beginning of the split.

    """
    def __init__(self):
        """Initialize and start the stopwatch."""
        self.start = time.time()
        self.prior = self.start

    def read(self, label):
        """Print out total elapsed time and split time."""
        now = time.time()
        elapsed = now - self.start
        split = now - self.prior
        self.prior = now
        print(f"{label:8s}: {split:7.2f}, {elapsed:7.2f} seconds")

    def reset(self):
        """Reset the start time."""
        self.start = time.time()
        self.prior = self.start
