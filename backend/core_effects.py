from .track import Track
from .effect import SingleEffect, SpliceEffect, MultiEffect

from pydub import AudioSegment


class DefaultSplice(SpliceEffect):
    """
    Splice a list of tracks together without modification
    """
    def __init__(self):
        super().__init__()

    def execute(self, tracks: list[Track]) -> Track:
        audio_segments: list[AudioSegment] = []
        for track in tracks:
            audio_segments.append(track.pydub_audio_segment)

        final_seg = audio_segments.pop()
        for segment in audio_segments:
            max_len = max(len(segment), len(final_seg))
            segment = segment + AudioSegment.silent(duration=max_len - len(segment))
            final_seg = final_seg + AudioSegment.silent(duration=max_len - len(final_seg))
            final_seg = final_seg.overlay(segment)

        final_seg = final_seg.normalize()

        final_track = Track(final_seg)

        return final_track
