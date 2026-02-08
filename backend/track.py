from os import PathLike

import librosa
import numpy as np
import soundfile as sf
from numba.np.arrayobj import np_array
from pydub import AudioSegment


class Track:
    def __init__(self, audio: PathLike | str | AudioSegment | np.ndarray, sample_rate: int = 44100):
        self.sample_rate = sample_rate

        if isinstance(audio, AudioSegment):
            # Sets self.samples and self.samplerate
            self.save_from_pydub_segment(audio)

        elif isinstance(audio, (str)):
            self.load_from_librosa(audio)
        elif isinstance(audio, np.ndarray):
            self.samples = audio
        else:
            raise TypeError("'audio' parameter must be a file path or an AudioSegment instance.")

        # Convert mono to stereo
        if self.samples.ndim == 1:
            self.samples = np.column_stack([self.samples, self.samples])
        elif self.samples.ndim != 2:
            raise ValueError("Audio input must be mono or stereo.")

        if self.sample_rate != 44100:
            self.resample()

    def __hash__(self):
        return hash(self.samples)

    def __eq__(self, other):
        if isinstance(other, Track):
            return self.__hash__() == other.__hash__()
        return False

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, array: np.array):
        # Ensure the shape is [num_samples, num_channels] (i.e., [N, 2] for stereo)
        if array.shape[0] == 2:
            array = array.T

        self._samples = array

    @property
    def num_channels(self):
        return self.samples.shape[0]

    @property
    def num_samples(self):
        return self.samples.shape[1]

    @property
    def duration(self):
        return self.num_samples / self.sample_rate

    @property
    def int16(self):
        return np.int16(self.samples * 32767)

    @property
    def pydub_audio_segment(self):
        return AudioSegment(
            self.int16.tobytes(),
            frame_rate=self.sample_rate,
            sample_width=2,
            channels=2
        )

    @staticmethod
    def int16_to_float32(int16_audio: np.array):
        return int16_audio.astype(np.float32) / 32767.0

    def load_from_librosa(self, audio: str | np.ndarray):
        """Load audio from a file using librosa"""
        # TODO: Probably redundant to use both calls
        self.samples, self.sample_rate = librosa.load(audio, dtype="float32", mono=False, sr=self.sample_rate)

    def save_from_pydub_segment(self, segment: AudioSegment):
        raw_audio = segment.raw_data

        # Load pcm into np.array
        int16_data = np.frombuffer(raw_audio, dtype=np.int16)

        # Convert to 2D array
        int16_data = int16_data.reshape(-1, 2)

        # Back to float32 :)
        self.samples = self.int16_to_float32(int16_data)
        print(self.samples.shape)
        if segment.frame_rate != self.sample_rate:
            self.resample()

    def get_chunks(self, sample_size: int, flatten=False):
        remainder = len(self.samples) % sample_size
        arr = self.samples
        if remainder != 0:
            arr = self.samples[:-remainder]

        split_arr = np.split(arr, int(len(arr) / sample_size))
        if flatten:
            for i, c in enumerate(split_arr):
                split_arr[i] = c.flatten()

        return split_arr

    def resample(self, target_rate: int = None):
        if self.sample_rate == target_rate:
            return

        if not target_rate:
            target_rate = self.sample_rate

        self.samples = librosa.resample(self.samples, orig_sr=self.sample_rate, target_sr=target_rate, axis=0).T
        self.sample_rate = target_rate

    def export(self, file_path):
        sf.write(file_path, self.samples, samplerate=self.sample_rate)
