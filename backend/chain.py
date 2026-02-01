from abc import ABC, abstractmethod
from uuid import uuid4

from backend.effect import Effect, SingleEffect
from backend.globals import audio_type
from backend.track import Track


class Chain(ABC):
    def __init__(self, name: str):
        self.id = uuid4()  # unique ID for this chain
        self.name = name  # human-readable name

    @abstractmethod
    def append_to_chain(self, *params):
        """ Add an effect to the chain """
        pass

    @abstractmethod
    def remove_from_chain(self, **params):
        """Remove an effect from the chain"""
        pass

    @abstractmethod
    def execute_chain(self) -> audio_type:
        """Execute every effect in the chain"""
        pass


class SingleChain(Chain):
    """
    Chain where every effect is tied to a single track.
    """
    def __init__(self, name: str, tracks: list[Track] = None):
        super().__init__(name)

        self.chain: dict[Track, list[Effect]] = dict()
        if tracks:
            for track in tracks:
                self.chain[track] = list()

    def append_to_chain(self, track: Track, effect: SingleEffect) -> bool:
        """

        :param track: Track the effect will apply to.
        :param effect: Effect instance.
        :return: True if chain was modified, otherwise False
        """
        if self.chain.get(track):
            if effect in self.chain[track]:
                self.chain[track].append(effect)
                return True
        else:  # If the track is new add it to the dict with an effect if the effect is not None
            self.chain[track] = [e for e in [effect] if e is not None]  # This is stupid but I love it
            return True
        return False

    def remove_from_chain(self, track: Track, effect: Effect):


    def execute_chain(self) -> audio_type:
        pass
