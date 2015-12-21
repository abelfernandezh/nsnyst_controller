""" nsnyst.controller

This module is in charge of controlling the flow of execution of the recording
process. Also is responsible of handling and integrating new data.
"""

__author__ = 'Roberto Antonio Becerra García'

from numpy import array


class Controller(object):
    """ Adquisition and stimulation controller
    """
    pass

    def __init__(self):
        """ Constructor
        """
        pass

    @classmethod
    def instance(cls):
        """ Singleton class instance
        """
        pass

    def start_recording(self):
        """ Start signal recording
        """
        pass

    def stop_recording(self):
        """ Stop signal recording
        """
        pass

    def receive_data(self, amplifier_data: array, stimulator_data: array):
        """ Process new data
        """
        pass


def handle_amplifier_data(amplifier_data: array):
    """ Handle new received data
    """
    pass
