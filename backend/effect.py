from enum import Enum
from abc import ABC, abstractmethod

from backend.globals import audio_type


class EffectMode(Enum):
    """
    Indicates how many tracks an effect expects and returns.
    SINGLE: Inputs a single track, outputs a single track.
    MULTI: Inputs multiple tracks, outputs multiple tracks.
    COMBINE: Inputs multiple tracks, outputs a single track.
    """
    SINGLE = 1
    MULTI = 2
    COMBINE = 3

    def expects_multiple_inputs(self):
        return self.value is not self.SINGLE


class Effect(ABC):
    def __init__(self, effect_type: EffectMode, audio: audio_type):
        self.expects_multiple = effect_type.expects_multiple_inputs()
        self.type = type
        self.audio = audio
        return

    @abstractmethod
    def go(self) -> audio_type:
        """
        Define your main
        :return:
        """
        pass


class SingleEffect(Effect, ABC):
    pass


class MultiEffect(Effect, ABC):
    pass


class CombineEffect(Effect, ABC):
    pass
