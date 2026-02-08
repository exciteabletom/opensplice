from backend.core_effects import DefaultSplice
from backend.track import Track


def main():
    folder = "/home/tom/Music/free_samples/"
    files = ["yeah.flac", "trombone.wav", "guirro.wav"]

    tracks = []
    for file in files:
        tracks.append(Track(folder + file))

    output = DefaultSplice().execute(tracks)
    print("exporting")
    output.export(folder + "out.wav")


if __name__ == '__main__':
    main()
