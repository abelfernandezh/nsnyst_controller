from enum import Enum
from collections import OrderedDict
from os.path import dirname
from math import radians
import json

from nsnyst.core import user_settings


class Channel(Enum):
    Both_Channels = 0
    Horizontal_Channel = 1
    Vertical_Channel = 2


class StimulusType(Enum):
    Saccadic = 0
    Pursuit = 1


class Stimulus:
    def __init__(self, name, duration, channel=Channel.Both_Channels):
        self.name = name
        self.channel = channel
        self.duration = duration


class SaccadicStimulus(Stimulus):
    def __init__(self, name, duration, amplitude, variation, fixation_duration, channel=Channel.Both_Channels):
        super(SaccadicStimulus, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.fixation_duration = fixation_duration
        self.variation = variation

    @property
    def information(self):
        information = OrderedDict()
        information['name'] = self.name
        information['duration'] = self.duration
        information['fixation_duration'] = self.fixation_duration
        information['amplitude'] = self.amplitude
        information['variation'] = self.variation
        information['channel'] = self.channel.value
        return information


class PursuitStimulus(Stimulus):
    def __init__(self, name, duration, amplitude, velocity, channel=Channel.Both_Channels):
        super(PursuitStimulus, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.velocity = velocity

    @property
    def information(self):
        stimulus = OrderedDict()
        stimulus['name'] = self.name
        stimulus['duration'] = self.duration
        stimulus['amplitude'] = self.amplitude
        stimulus['velocity'] = self.velocity
        stimulus['channel'] = self.channel.value
        return stimulus


class Protocol:
    def __init__(self, name, notes, distance):
        self.protocol_name = name
        self.protocol_notes = notes
        self.subject_distance = distance
        self.stimuli = []

    @property
    def name(self):
        return self.protocol_name

    @property
    def notes(self):
        return self.protocol_notes

    @property
    def distance(self):
        return self.subject_distance

    @property
    def information(self):
        protocol = OrderedDict()
        protocol['name'] = self.name
        protocol['notes'] = self.notes
        protocol['distance'] = self.subject_distance
        protocol['stimuli'] = []

        for stimulus in self.stimuli:
            if type(stimulus) == SaccadicStimulus:
                s_type = StimulusType.Saccadic
            else:
                s_type = StimulusType.Pursuit

            protocol['stimuli'].append([s_type.name, stimulus.information])

        return protocol

    def add_stimulus(self, stimulus):
        self.stimuli.append(stimulus)
