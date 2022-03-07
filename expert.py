"""
Usage: python expert.py <audio file>
"""

import sys
import os

from pydub import AudioSegment
import matplotlib.pyplot as plt

from audio_to_midi_melodia import audio_to_midi_melodia as atmm

YES_MSG = "The Lick"
NO_MSG = "Not The Lick"

if len(sys.argv) < 2:
    print("Usage: python expert.py <audio file>")
    exit(0)

def is_lick(note_list):
    notes = note_list[:]
    
    pitches = [int(z) for _, _, z in notes]
    min_pitch = min(pitches)
    
    # normalize notes so the lowest note is 0
    pitches = [x - min_pitch for x in pitches]
    print(f"pitches: {pitches}")
    
    if len(notes) < 6:
        return False
    elif len(notes) == 6:
        # if it has 6 notes, it better be scale degrees 3 4 5 3 1 2
        possible_norms = [
            [4, 5, 7, 4, 0, 2],
            [2, 4, 5, 7, 0, 2]
        ]

        for norm in possible_norms:
            print(f"norm:    {norm}")
            if norm == pitches:
                return True
        
        return False
    elif len(notes) == 7:
        # if it has 7 notes, it better be 2 3 4 5 3 1 2
        possible_norms = [
            [2,4,5,7,4,0,2]
        ]

        for norm in possible_norms:
            if norm == pitches:
                return True
        
        return False

    # if the first 5 notes are all ascending, treat teh first note as a grace note
    # check that the tones after the first 4 or 5 follow on-net a steeper, negative slope
    # check that the last note is the same as either the first or second, first if only the first 4 notes ascend, second if the first 5 notes ascend

    return False

def classify(audio_file, show_graphic=False):
    # notes is a list of tuples that have the form (note_start_time, note_length, note_pitch)
    a_s = AudioSegment.from_file(audio_file)

    length = len(a_s) / 1000 # in seconds

    print(f"minduration: ", length/30)

    notes = atmm(audio_file, minduration=length/50)
    print(notes)

    ans = YES_MSG if is_lick(notes) else NO_MSG

    # start times and note values
    xs = [x for x, _, _ in notes]
    ys = [z for _, _, z in notes]

    # add the duration for the final note
    ys.append(ys[-1])
    xs.append(xs[-1] + notes[-1][1])

    if show_graphic:
        plt.step(xs, ys, where='post') # kind of close to looking like midi lol
        plt.title(ans)
        plt.show()
    else:
        print(f"{audio_file}: {ans}")


if os.path.isdir(sys.argv[1]):
    directory = sys.argv[1]

    for item in os.listdir(directory):
        classify(f"{directory}/{item}", show_graphic=False)
else:
    classify(sys.argv[1], show_graphic=True)