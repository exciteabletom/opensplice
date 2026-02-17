"""
Different types of effect chains.

SingleChain:
            Track  -> Effect\
                   -> Effect >>  -> Output Track
                   -> Effect/
            Track ...

MultiChain:
             Effect -> Track \
                    -> Track  >>  -> Output Track
                    -> Track /
             Effect ...

SpliceChain:
            Track \
            Track  \
            Track   >> Effect -> Output Track
            Track  /
            Track /
"""

from abc import ABC, abstractmethod
from uuid import uuid4

from .effect import Effect, SingleEffect, MultiEffect, SpliceEffect
from .track import Track

SingleChainType = dict[Track, list[Effect]]  # Every track has multiple effects
MultiChainType = dict[Effect, list[Track]]  # Every effect has multiple effects


class Chain(ABC):
    """
    Chains deal with only one form of effect, (single, multi, splice).
    Chains are a generic structure which links effects to tracks and executes them in a predictable order.
    """

    @abstractmethod
    def __init__(self, name: str):
        self.id = uuid4()  # unique ID for this chain
        self.name = name  # human-readable name
        self.chain: dict[object, list] = {}

    @abstractmethod
    def remove_parent(self, parent):
        self.chain.pop(parent)

    @abstractmethod
    def remove_child(self, parent, child):
        """Remove from the chain"""
        self.chain[parent].remove(child)

    @abstractmethod
    def append_to_chain(self, parent, child):
        """Add to the chain"""
        if self.chain.get([parent]):
            if child in self.chain[parent]:
                self.chain[parent].append(child)
        else:  # If the effect is new add it to the dict with a track if the track is not None
            self.chain[parent] = [
                c for c in [child] if c is not None
            ]  # This is stupid but I love it

    @abstractmethod
    def change_child_order(self, parent, child, index: int):
        """Move an effect to a different position in the chain."""
        if index < 0 or index > len(self.chain[parent]):
            raise ValueError(
                f"Index -> {index} <-, cannot be greater than chain length or < 0."
            )

        try:
            self.chain[parent].index(child)
        except KeyError:
            raise ValueError(f"Parent ->{parent}<- does not exist in this chain.")
        except ValueError:
            raise ValueError(
                f"Child ->{child}<- is not attached to parent ->{parent}<- in this chain."
            )

        self.chain[parent].remove(child)
        self.chain[parent].insert(index, child)

    @abstractmethod
    def execute_chain(self, *args, **kwargs):
        """Execute every effect in the chain"""
        pass


class SingleChain(Chain):
    """
    Chain for SingleEffect classes, every effect is tied to a single track.
    """

    def __init__(self, name: str):
        super().__init__(name)

        self.chain: dict[Track, list[Effect]] = dict()

    def remove_parent(self, track: Track):
        super().remove_parent(track)

    def remove_child(self, track: Track, effect: SingleEffect):
        super().remove_child(track, effect)

    def change_child_order(self, track: Track, effect: SingleEffect, index: int):
        super().change_child_order(track, effect, index)

    def append_to_chain(self, track: Track, effect: SingleEffect):
        """

        :param track: Track the effect will apply to.
        :param effect: Effect instance.
        """
        if len(self.chain[track]) > 1:
            raise ValueError("Tracks and SingleEffects have a 1 -> 1 relationship.")
        super().append_to_chain(track, effect)

    def execute_chain(self):
        """
        Execute every effect in a chain in order.
        :return:
        """
        for track, effects in self.chain:
            for effect in effects:
                effect.execute(track)


class MultiChain(Chain):
    """
    Chain for MultiEffect classes, every effect is tied to multiple tracks.
    """

    effect_type = MultiEffect

    def __init__(self, name: str):
        super().__init__(name)
        self.chain: MultiChainType = dict()
        effect_type = MultiEffect

    def remove_parent(self, effect: effect_type):
        super().remove_parent(effect)

    def remove_child(self, effect: effect_type, track: Track):
        super().remove_child(effect, track)

    def change_child_order(self, effect: effect_type, track: Track, index: int):
        super().change_child_order(effect, track, index)

    def append_to_chain(self, effect: effect_type, track: Track):
        """
        Append a MultiEffect and linked input track.

        :param track: Track to add to the effect's input.
        :param effect: Effect instance.
        """
        super().append_to_chain(effect, track)

    def execute_chain(self):
        for effect, tracks in self.chain:
            effect.execute(tracks)


class SpliceEffectChain(MultiChain):
    """"""

    effect_type = SpliceEffect

    def __init__(self, name: str):
        super().__init__(name)
        super().effect_type = SpliceEffect

    def execute_chain(self):
        for effect, tracks in self.chain:
            effect.execute(tracks)
