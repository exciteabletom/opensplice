from backend.core_effects import DefaultSplice, SimilaritySplice
from backend.track import Track


def main():
    folder = "/home/tom/Music/free_samples/"
    files = ["yeah.flac", "trombone.wav", "guirro.wav", "2000.flac", "happiness.mp3"]

    tracks = []
    for file in files:
        tracks.append(Track(folder + file))

    output = SimilaritySplice().execute(tracks)
    print("exporting")
    output.export(folder + "out.wav")


if __name__ == '__main__':
    main()
