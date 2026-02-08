from abc import ABC

import librosa
import numpy as np
from audioread.ffdec import available

from .track import Track
from .effect import SingleEffect, SpliceEffect, MultiEffect

from pydub import AudioSegment
from sklearn.neighbors import BallTree


class DefaultSplice(SpliceEffect):
    """
    Splice a list of tracks together without modification
    """

    def __init__(self):
        super().__init__()

    def execute(self, tracks: list[Track]) -> Track:
        tracks = self.equalise_track_length(tracks)

        audio_segments: list[AudioSegment] = []
        for track in tracks:
            audio_segments.append(track.pydub_audio_segment)

        final_seg = audio_segments.pop()

        for segment in audio_segments:
            final_seg = final_seg.overlay(segment)

        final_seg = final_seg.normalize()

        final_track = Track(final_seg)

        return final_track


class SimilaritySplice(SpliceEffect):
    def __init__(self):
        super().__init__()

    def execute(self, tracks: list[Track]) -> Track:
        sample_size = 20000
        target = tracks.pop()
        target_slices = target.get_chunks(sample_size, True)

        available_slices = []
        for t in tracks:
            for c in t.get_chunks(sample_size, True):
                available_slices.append(c)

        available_slices = np.array(available_slices)
        tree = BallTree(np.array(available_slices, dtype=np.float32))

        final_slices = []
        for t in target_slices:
            index = tree.query(t.reshape(1, -1), return_distance=False, dualtree=True)[0][0]
            final_slices.append(available_slices[index])

        final_slices = np.array(final_slices, dtype="float32")
        final_slices = final_slices.flatten()
        final_slices = final_slices.reshape((int(len(final_slices) / 2), 2))

        return Track(final_slices, target.sample_rate)
