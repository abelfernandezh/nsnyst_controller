from enum import Enum


class Channel(Enum):
    Horizontal_Channel = 1
    Vertical_Channel = 2


class Stimuli:
    def __init__(self, name, duration, channel=0):
        self.name = name
        self.chanel = channel
        self.duration = duration


class SaccadicStimuli(Stimuli):
    def __init__(self, name, duration, amplitude, velocity, channel=0):
        super(SaccadicStimuli, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.velocity = velocity


class FixationStimuli(Stimuli):
    def __init__(self, name, duration, amplitude, fixation_duration, variation, channel=0):
        super(FixationStimuli, self).__init__(name, duration, channel)
        self.amplitude = amplitude
        self.fixation_duration = fixation_duration
        self.variation = variation
