"""
There are 3 types of effects:
    SingleEffect - Applies an effect to one track and returns one track.
    MultiEffect - Applies an effect to multiple tracks and returns multiple tracks.
    SpliceEffect - Applies an effect to multiple tracks and returns one track.
"""
from abc import ABC, abstractmethod

from .track import Track


class Effect(ABC):
    def __init__(self):
        self.settings = {}

    @abstractmethod
    def execute(self, track: Track) -> Track:
        """
        Do stuff.
        """
        pass


class SingleEffect(Effect, ABC):
    pass


class MultiEffect(Effect, ABC):
    pass


class SpliceEffect(MultiEffect, ABC):
    pass
