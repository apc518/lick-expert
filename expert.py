"""
Usage: python expert.py <audio file>
"""

import sys

import matplotlib.pyplot as plt

from audio_to_midi_melodia import audio_to_midi_melodia as atmm

if len(sys.argv) < 2:
    print("Usage: python expert.py <audio file>")
    exit(0)

audio_file = sys.argv[1]

notes = atmm(audio_file)
print(notes)

# start times and note values
xs = [x for x, _, _ in notes]
ys = [z for _, _, z in notes]

# add the duration for the final note
ys.append(ys[-1])
xs.append(xs[-1] + notes[-1][1])

plt.step(xs, ys, where='post') # kind of close to midi looking I guess lol
plt.show()