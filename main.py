from backend.core_effects import DefaultSplice, SimilaritySplice
from backend.track import Track


def main():
    folder = "/home/tom/Music/free_samples/"
    #files = glob("/home/tom/Music/free_samples/*")
    # files = ["System of a Down/Toxicity (Disc 1)/01 - System of a Down - Toxicity (Disc 1) - Prison Song.flac", "free_samples/2000.flac"]
    #files = ("2000.flac", "happiness.mp3")
    files = ("futurebreed.flac", "beneath.flac", "soulburn.flac") #"happiness.mp3")

    tracks = []
    for file in files:
        tracks.append(Track(folder + file))

    output = SimilaritySplice(multiprocessing=False).execute(tracks)
    print("exporting")
    output.export(folder + "out.wav")


if __name__ == "__main__":
    main()
