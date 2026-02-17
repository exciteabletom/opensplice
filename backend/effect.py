"""
There are 3 types of effects:
    SingleEffect - Applies an effect to one track and returns one track.
    MultiEffect - Applies an effect to multiple tracks and returns multiple tracks.
    SpliceEffect - Applies an effect to multiple tracks and returns one track.
"""

from abc import ABC, abstractmethod

import numpy
import numpy as np

from .track import Track


class Effect(ABC):
    def __init__(self):
        self._settings = {}

    @staticmethod
    def equalise_track_length(tracks: list[Track]):
        longest = max([i.num_samples for i in tracks])
        edited_tracks = []
        for track in tracks:
            if track.num_samples == longest:
                continue
            zero_array = numpy.zeros(track.num_samples - longest, 2)
            track.samples = np.append(track.samples, zero_array)
        return tracks

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
