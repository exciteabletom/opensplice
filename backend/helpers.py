import librosa
import numpy as np


def get_flat_ffts(audio: np.ndarray, **kwargs) -> np.ndarray:
    stft = librosa.stft(audio, **kwargs)
    stft = np.abs(stft)
    return stft.flatten()
