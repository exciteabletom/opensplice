import os
import random
from itertools import starmap
from multiprocessing import Pool, cpu_count
from multiprocessing.util import close_all_fds_except

import numpy as np
from sklearn.utils.sparsefuncs_fast import csr_matmul_csr_to_dense

from .helpers import get_flat_ffts
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
    def __init__(self, multiprocessing=True):
        super().__init__()
        self._settings["multiprocessing"] = multiprocessing
        self.from_chunks = []
        self.from_chunks_fft = []
        self.to_chunks = []
        self.to_chunks_fft = []
        self.tree = None

    def execute(self, tracks: list[Track]) -> Track:
        sample_size = 12000
        target = tracks.pop()

        self.to_chunks = target.get_chunks(sample_size, True)
        self.to_chunks_fft = [get_flat_ffts(c) for c in self.to_chunks]
        self.from_chunks = []
        self.from_chunks_fft = []

        for t in tracks:
            for c in t.get_chunks(sample_size, True):
                self.from_chunks.append(c)
                self.from_chunks_fft.append(get_flat_ffts(c))

        self.tree: BallTree = BallTree(self.from_chunks_fft)

        final_chunks = []

        if self._settings["multiprocessing"]:
            with Pool(processes=2) as pool:
                neighbour_pairs = pool.map(
                    self._get_nearest_neighbour_pair, self.to_chunks_fft
                )

            print("SimilaritySplice: Found neighbour pairs")

            with Pool(processes=os.cpu_count()) as pool:
                final_chunks = pool.starmap(
                    self._process_closest_chunk_from_neighbour_pair, neighbour_pairs
                )

        else:
            neighbour_pairs = list(map(
                self._get_nearest_neighbour_pair, self.to_chunks_fft
            ))

            print("SimilaritySplice: Found neighbour pairs")

            final_chunks = list(starmap(
                self._process_closest_chunk_from_neighbour_pair, neighbour_pairs
            ))

        print("SimilaritySplice: Generated final chunks")

        final_chunks = np.array(final_chunks, dtype="float32")
        final_chunks = final_chunks.flatten()
        final_chunks = final_chunks.reshape((int(len(final_chunks) / 2), 2))

        return Track(final_chunks, target.sample_rate)

    def _get_nearest_neighbour_pair(self, to_chunk_fft):
        nearest_neighbour_index = self.tree.query(
            [to_chunk_fft], k=1, return_distance=False, dualtree=True
        )[0][0]

        return to_chunk_fft, nearest_neighbour_index

    def _process_closest_chunk_from_neighbour_pair(self, to_chunk_fft, index):
        closest_fft = self.from_chunks_fft[index]
        closest_fft_mean = np.mean(closest_fft)
        to_fft_mean = np.mean(to_chunk_fft)

        if (closest_fft_mean == 0) or (to_fft_mean == 0):
            multiplier = 0.0
        else:
            multiplier = to_fft_mean / closest_fft_mean

        closest_chunk = self.from_chunks[index]

        closest_chunk = closest_chunk * multiplier

        return closest_chunk
