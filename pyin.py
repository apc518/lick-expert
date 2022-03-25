import sys
import os

import numpy as np
import librosa
import vamp
import matplotlib.pyplot as plt

from audio_to_midi_melodia import hz2midi, midi_to_notes

def graph_array(arr):
    plt.plot(np.linspace(0, len(arr), len(arr)), arr)
    plt.show()


def graph_notes(notes):
    # start times and note values
    xs = [x for x, _, _ in notes]
    ys = [z for _, _, z in notes]

    # add the duration for the final note
    ys.append(ys[-1])
    xs.append(xs[-1] + notes[-1][1])

    plt.step(xs, ys, where='post') # kind of close to looking like midi lol
    plt.show()

def smooth_array(arr):
    """
    remove anomalies
    not implemented yet
    """

    return arr

def pyin_getnotes(infile):
    fs = 44100
    hop = 128
    smooth = 0.25
    minduration = 0.1

    data, sr = librosa.load(infile, sr=44100)
        
    # mixdown to mono if needed
    if len(data.shape) > 1 and data.shape[1] > 1:
        data = data.mean(axis=1)

    old_stdout = sys.stdout
    sys.stdout = open(os.devnull, "w")
    audio = vamp.collect(data, sr, "pyin:pyin")
    sys.stdout = old_stdout

    pitch = audio['list']


    hz = np.zeros(len(pitch))

    for i, p in enumerate(pitch):
        if 'values' in p:
            hz[i] = p['values'][0]

    # graph_array(hz)


    midi_pitch = hz2midi(hz)
    notes = midi_to_notes(midi_pitch, fs, hop, smooth, minduration)
    # graph_notes(notes)

    return notes


if __name__ == "__main__":
    print(pyin_getnotes("p/ezlick.wav"))