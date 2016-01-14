from enum import Enum
from numpy import array
import json


class Channel(Enum):
    Horizontal_Channel = 1
    Vertical_Channel = 2


class Stimulus:
    def __init__(self, name, duration, channel=0):
        self.name = name
        self.chanel = channel
        self.duration = duration


class SaccadicStimulus(Stimulus):
    def __init__(self, name, duration, amplitude, velocity, channel=0):
        super(SaccadicStimulus, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.velocity = velocity


class FixationStimulus(Stimulus):
    def __init__(self, name, duration, amplitude, fixation_duration, variation, channel=0):
        super(FixationStimulus, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.fixation_duration = fixation_duration
        self.variation = variation


class Protocol:
    def __init__(self, name, notes):
        self.protocol_name = name
        self.protocol_notes = notes
        self.stimuli = array()

    @property
    def name(self):
        return self.protocol_name

    @property
    def notes(self):
        return self.protocol_notes

    @property
    def information(self):
        protocol = []
        protocol.name = self.name
        protocol.notes = self.notes
        protocol.stimuli = array()

        for stimulus in self.stimuli:
            break

    def add_stimulus(self, stimulus):
        self.stimuli.append(stimulus)

    def save(self):
        pass
