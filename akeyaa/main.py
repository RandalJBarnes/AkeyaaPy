"""

Design Approach
---------------
This program is constructed using an adaptation of the classic
Model/View/Controller (MVC) design pattern.

* The Model
    - The model owns the data.
    - The model is responsible for retrieving the venue and well data.
    - The model is responsible for archiving results from a run.
    - The model carries out the computations.
    - The model has no knowledge of the Controller or View.
    - The model is essentially a standalone program with a defined API.

* The View
    - The view controls what is seen on the screen.
    - The view owns all of the widgets.
    - The view owns all of the on-screen graphics.
    - The view embraces a specific UI protocol (e.g. tkinter).
    - The view hides all details of the UI from the controller.
    - The view has no knowledge of the Model.
    - The view interacts with the controller via a callback.

* The Controller
    - The controller owns the model instance.
    - The controller owns the view instance.
    - The controller is the interface between the model and the view.
    - The controller has no knowledge of the UI protocol.

"""
from akeyaa.controller.controller import Controller


__author__ = "Randal J Barnes"
__version__ = "06 August 2020"


def main():
    control = Controller()



if __name__ == "__main__":
    # execute only if run as a script
    main()


