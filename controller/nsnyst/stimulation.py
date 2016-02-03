from enum import Enum
from os.path import dirname
from math import radians
import json

from core import user_settings


class Channel(Enum):
    Horizontal_Channel = 1
    Vertical_Channel = 2


class StimulusType(Enum):
    Saccadic = 0
    Pursuit = 1


class Stimulus:
    def __init__(self, name, duration, channel=0):
        self.name = name
        self.channel = channel
        self.duration = duration


class SaccadicStimulus(Stimulus):
    def __init__(self, name, duration, amplitude, variation, fixation_duration, channel=0):
        super(SaccadicStimulus, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.fixation_duration = fixation_duration
        self.variation = variation

    @property
    def information(self):
        information = {'name': self.name, 'duration': self.duration, 'fixation_duration': self.fixation_duration,
                       'amplitude': self.amplitude, 'variation': self.variation, 'channel': self.channel}
        if self.channel != 0:
            information['channel'] = self.channel.value
        return information


class PursuitStimulus(Stimulus):
    def __init__(self, name, duration, amplitude, velocity, channel=0):
        super(PursuitStimulus, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.velocity = velocity

    @property
    def information(self):
        stimulus = {'name': self.name, 'duration': self.duration, 'amplitude': self.amplitude,
                    'velocity': self.velocity, 'channel': self.channel}
        if self.channel != 0:
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
        protocol = {'name': self.name, 'notes': self.notes, 'saccadic_stimuli': [], 'pursuit_stimuli': []}

        for stimulus in self.stimuli:
            if type(stimulus) == SaccadicStimulus:
                protocol['saccadic_stimuli'].append(stimulus.information)
            else:
                protocol['pursuit_stimuli'].append(stimulus.information)

        return protocol

    def add_stimulus(self, stimulus):
        self.stimuli.append(stimulus)

    def save(self):
        path = user_settings.value('workspace_path', dirname(__file__))
        json.dump(self.information, open(path + '/' + self.name + '.json', 'w'), sort_keys=False, indent=4)
