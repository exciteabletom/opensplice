from os import PathLike


class Track:
    def __init__(self, audio_path: PathLike):
        self.audio_file = open(audio_path)
        self.audio_data = self.audio_file.read()  # TODO
        pass

    def __hash__(self):
        return hash(self.audio_data)

    def __eq__(self, other):
        if isinstance(other, Track):
            return self.__hash__() == other.__hash__()
        return False
