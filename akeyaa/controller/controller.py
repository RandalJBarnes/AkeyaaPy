"""Implement the Controller class in the MVC pattern for AkeyaaPy."""

from akeyaa.model.model import Model
from akeyaa.view.view import View

__author__ = "Randal J Barnes"
__version__ = "07 August 2020"


class Controller:
    def __init__(self):

        self.model = Model()
        self.venue_data = self.model.get_venue_data()
        self.parameters = self.model.get_parameters()

        self.view = View(self.parameters, self.venue_data)
        self.view.start()

