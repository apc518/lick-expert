"""
Created by Justin Salamon <justin.salamon@nyu.edu>, 2015-11-09

Modified by Andy Chamberlain <andychamberlainmusic@gmail.com>, 2022-03-02

I (Andy Chamberlain) simply removed some imports and functions I don't need, and made the script compatible with mp3 files and python 3

Justin Salamon implemented all the logic.
"""

# CREATED: 11/9/15 3:57 PM by Justin Salamon <justin.salamon@nyu.edu>
# MODIFIED: 2022-03-02 by Andy Chamberlain <andychamberlainmusic@gmail.com>

import warnings
import librosa
import vamp
import argparse
import numpy as np
from scipy.signal import medfilt

'''
Extract the melody from an audio file.

The script extracts the melody from an audio file using the Melodia algorithm,
and then segments the continuous pitch sequence into a series of quantized
notes.

Note: Melodia can work pretty well and is the result of several years of
research. The note segmentation/quantization code was hacked in about 30
minutes. Proceed at your own risk... :)

usage: audio_to_midi_melodia.py [-h] [--smooth SMOOTH]
                                [--minduration MINDURATION] [--jams]
                                infile

Examples:
python audio_to_midi_melodia.py --smooth 0.25 --minduration 0.1 --jams
                                ~/song.wav ~/song.mid 60
'''

INF = 2**32


def midi_to_notes(midi, fs, hop, smooth, minduration):

    # smooth midi pitch sequence first
    if (smooth > 0):
        filter_duration = smooth  # in seconds
        filter_size = int(filter_duration * fs / float(hop))
        if filter_size % 2 == 0:
            filter_size += 1
        midi_filt = medfilt(midi, filter_size)
    else:
        midi_filt = midi
    # print(len(midi),len(midi_filt))

    notes = []
    p_prev = -INF
    duration = 0
    onset = 0
    for n, p in enumerate(midi_filt):
        if p == p_prev:
            duration += 1
        else:
            # treat 0 as silence
            if p_prev > 0:
                # add note
                duration_sec = duration * hop / float(fs)
                # only add notes that are long enough
                if duration_sec >= minduration:
                    onset_sec = onset * hop / float(fs)
                    notes.append((onset_sec, duration_sec, p_prev))

            # start new note
            onset = n
            duration = 1
            p_prev = p

    # add last note
    if p_prev > 0:
        # add note
        duration_sec = duration * hop / float(fs)
        onset_sec = onset * hop / float(fs)
        notes.append((onset_sec, duration_sec, p_prev))

    return notes


def hz2midi(hz):

    # convert from Hz to midi note
    hz_nonneg = hz.copy()
    idx = hz_nonneg <= 0
    hz_nonneg[idx] = 1
    midi = 69 + 12*np.log2(hz_nonneg/440.)
    midi[idx] = 0

    # round
    midi = np.round(midi)

    return midi


def audio_to_midi_melodia(infile, smooth=0.25, minduration=0.1, print_progress=False):

    # define analysis parameters
    fs = 44100
    hop = 128

    # load audio using librosa
    if print_progress: print("Loading audio...")
    warnings.filterwarnings('ignore') # ignore librosa warning
    data, sr = librosa.load(infile, sr=44100)
    
    # mixdown to mono if needed
    if len(data.shape) > 1 and data.shape[1] > 1:
        data = data.mean(axis=1)

    # extract melody using melodia vamp plugin
    if print_progress: print("Extracting melody f0 with MELODIA...")
    melody = vamp.collect(data, sr, "mtg-melodia:melodia",
                          parameters={"voicing": 0.2})

    # hop = melody['vector'][0]
    pitch = melody['vector'][1]

    # impute missing 0's to compensate for starting timestamp
    pitch = np.insert(pitch, 0, [0]*8)

    # debug
    # np.asarray(pitch).dump('f0.npy')
    # print(len(pitch))

    # convert f0 to midi notes
    if print_progress: print("Converting Hz to MIDI notes...")
    midi_pitch = hz2midi(pitch)

    # segment sequence into individual midi notes
    notes = midi_to_notes(midi_pitch, fs, hop, smooth, minduration)

    return notes


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("infile", help="Path to input audio file.")
    parser.add_argument("--smooth", type=float, default=0.25,
                        help="Smooth the pitch sequence with a median filter "
                             "of the provided duration (in seconds).")
    parser.add_argument("--minduration", type=float, default=0.1,
                        help="Minimum allowed duration for note (in seconds). "
                             "Shorter notes will be removed.")

    args = parser.parse_args()

    audio_to_midi_melodia(args.infile, smooth=args.smooth,
                            minduration=args.minduration, savejams=args.jams, print_progress=True)
