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

    @property
    def information(self):
        information = []
        information.name = self.name
        information.duration = self.duration
        information.amplitude = self.amplitude
        information.velocity = self.velocity
        information.channel = self.chanel
        return information


class FixationStimulus(Stimulus):
    def __init__(self, name, duration, amplitude, fixation_duration, variation, channel=0):
        super(FixationStimulus, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.fixation_duration = fixation_duration
        self.variation = variation

    @property
    def information(self):
        information = []
        information.name = self.name
        information.duration = self.duration
        information.amplitude = self.amplitude
        information.fixation_duration = self.fixation_duration
        information.variation = self.variation
        return information


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
        protocol.saccadic_stimuli = array()
        protocol.fixation_stimuli = array()

        for stimulus in self.stimuli:
            if type(stimulus) == SaccadicStimulus:
                protocol.saccadic_stimuli.append(stimulus)
            else:
                protocol.fixation_stimuli.append(stimulus)

    def add_stimulus(self, stimulus):
        self.stimuli.append(stimulus)

    def save(self):
        pass
